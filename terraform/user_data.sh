#!/bin/bash
# User data script for EC2 initialization
# This runs once when the instance starts

set -e
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "=== Oil Spill Detection App - EC2 Initialization ==="
echo "Start time: $(date)"

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y \
  curl \
  wget \
  git \
  python3 \
  python3-pip \
  python3-venv \
  docker.io \
  docker-compose \
  awscli \
  mysql-client \
  htop \
  tmux \
  unzip \
  build-essential \
  libssl-dev \
  libffi-dev \
  python3-dev \
  libmysqlclient-dev

# Start Docker daemon
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Create application directory
APP_DIR="/opt/oil-spill-app"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone repository (update with your repo URL)
# git clone https://github.com/your-username/oil-spill-detection.git .

# Create .env file from Secrets Manager
echo "=== Fetching secrets from AWS Secrets Manager ==="
aws secretsmanager get-secret-value \
  --secret-id oil-spill-app/db-credentials \
  --region ${aws_region} \
  --query SecretString \
  --output text > /tmp/db_secrets.json

# Extract credentials and create .env
DB_HOST=$(jq -r '.host' /tmp/db_secrets.json)
DB_USER=$(jq -r '.username' /tmp/db_secrets.json)
DB_PASSWORD=$(jq -r '.password' /tmp/db_secrets.json)
DB_NAME=$(jq -r '.dbname' /tmp/db_secrets.json)

cat > $APP_DIR/.env << EOF
FLASK_ENV=production
DB_HOST=$DB_HOST
DB_PORT=3306
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=$DB_NAME
AWS_REGION=${aws_region}
AWS_S3_BUCKET=${s3_bucket}
EOF

chmod 600 $APP_DIR/.env

# Set up CloudWatch Logs agent
echo "=== Setting up CloudWatch Logs ==="
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb

# Create CloudWatch agent configuration
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/oil-spill-app/app.log",
            "log_group_name": "${cloudwatch_log_group}",
            "log_stream_name": "{instance_id}/app.log"
          },
          {
            "file_path": "/var/log/docker*.log",
            "log_group_name": "${cloudwatch_log_group}",
            "log_stream_name": "{instance_id}/docker.log"
          }
        ]
      }
    }
  },
  "metrics": {
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {
            "name": "cpu_usage_idle",
            "rename": "CPU_IDLE",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": [
          {
            "name": "used_percent",
            "rename": "DISK_USED",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60
      },
      "mem": {
        "measurement": [
          {
            "name": "mem_used_percent",
            "rename": "MEM_USED",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a query -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s

# Create log directory
mkdir -p /var/log/oil-spill-app
chown ubuntu:ubuntu /var/log/oil-spill-app

# Wait for RDS to be ready (with retry logic)
echo "=== Waiting for RDS database ==="
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
  if mysql -h "${db_host}" -u "${db_user}" -p"${db_password}" -e "SELECT 1" &> /dev/null; then
    echo "RDS database is ready!"
    break
  else
    echo "Attempt $attempt/$max_attempts: RDS not ready, waiting..."
    sleep 10
    ((attempt++))
  fi
done

if [ $attempt -gt $max_attempts ]; then
  echo "ERROR: RDS not ready after $max_attempts attempts"
  exit 1
fi

# Start application with docker-compose
echo "=== Starting application with Docker Compose ==="
cd $APP_DIR
# docker-compose up -d

# Create systemd service for docker-compose
cat > /etc/systemd/system/oil-spill-app.service << EOF
[Unit]
Description=Oil Spill Detection Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
RemainAfterExit=true
User=ubuntu
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable oil-spill-app
systemctl start oil-spill-app

# Install and configure log rotation
cat > /etc/logrotate.d/oil-spill-app << EOF
/var/log/oil-spill-app/app.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload oil-spill-app > /dev/null 2>&1 || true
    endscript
}
EOF

# Set up daily security updates
apt-get install -y unattended-upgrades
systemctl enable unattended-upgrades

echo "=== EC2 Initialization Complete ==="
echo "End time: $(date)"
