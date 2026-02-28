# Oil Spill Detection - AWS EC2 Deployment Guide

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Deployment with Docker](#local-deployment-with-docker)
3. [AWS Infrastructure Setup with Terraform](#aws-infrastructure-setup-with-terraform)
4. [EC2 Deployment](#ec2-deployment)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)
7. [Security Best Practices](#security-best-practices)

---

## Pre-Deployment Checklist

### Required Tools
- [ ] Docker & Docker Compose
- [ ] AWS CLI (v2)
- [ ] Terraform (>= 1.0)
- [ ] Python 3.10+
- [ ] Git

### AWS Account Requirements
- [ ] AWS account with appropriate IAM permissions
- [ ] EC2, RDS, S3, VPC, CloudWatch access
- [ ] ACM certificate (for HTTPS)
- [ ] SSH key pair created in EC2

### Application Configuration
- [ ] All `.env.example` files reviewed and updated
- [ ] Google OAuth credentials obtained (if using portal)
- [ ] Roboflow API key obtained
- [ ] Database credentials set securely
- [ ] S3 bucket name unique and available

---

## Local Deployment with Docker

### 1. Quick Start

```bash
# Clone repository
git clone https://github.com/your-username/oil-spill-detection.git
cd oil-spill-detection

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Make scripts executable
chmod +x scripts/*.sh

# Deploy with Docker Compose
./scripts/deploy_docker.sh
```

### 2. Environment Variables

Create `.env` file:

```env
# Database
DB_HOST=mysql
DB_PORT=3306
DB_USER=oil_spill_user
DB_PASSWORD=your_secure_password_here
DB_ROOT_PASSWORD=root_secure_password

# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=generate_with_$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_DEBUG=False

# AWS (optional, for S3 uploads)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name

# Google OAuth (for portal)
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/google/callback

# Roboflow
ROBOFLOW_API_KEY=your_roboflow_key
```

### 3. Verify Deployment

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f oil_spill_app

# Test APIs
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health

# Stop containers
docker-compose down
```

---

## AWS Infrastructure Setup with Terraform

### 1. Install Terraform

**macOS:**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Linux:**
```bash
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

**Windows (PowerShell):**
```powershell
choco install terraform
```

### 2. Configure Terraform

```bash
# Navigate to terraform directory
cd terraform

# Copy tfvars template
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**terraform.tfvars:**
```hcl
aws_region             = "us-east-1"
app_name               = "oil-spill-app"
environment            = "prod"
instance_type          = "t3.medium"
instance_count         = 1

# Database
db_instance_type       = "db.t3.small"
db_allocated_storage   = 50
db_multi_az            = true
db_backup_retention_days = 30
db_username            = "oil_spill_user"
db_password            = "VERY_SECURE_PASSWORD_MIN_16_CHARS"

# S3 bucket (must be globally unique)
s3_bucket_name         = "oil-spill-app-uploads-$(date +%s)"

# SSH Access (restrict to your IP)
ssh_allowed_cidrs      = ["YOUR_IP/32"]
```

### 3. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review changes
terraform plan -out=tfplan

# Review output carefully, then apply
terraform apply tfplan

# Save outputs
terraform output > ../infrastructure_outputs.json

# Verify deployment
terraform show
```

### 4. Get Infrastructure Details

```bash
# Extract important outputs
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
S3_BUCKET=$(terraform output -raw s3_bucket_name)
VPC_ID=$(terraform output -raw vpc_id)

echo "RDS: $RDS_ENDPOINT"
echo "S3 Bucket: $S3_BUCKET"
echo "VPC: $VPC_ID"
```

---

## EC2 Deployment

### 1. Get EC2 Instance IP

```bash
# List all running instances
aws ec2 describe-instances \
  --region us-east-1 \
  --query 'Reservations[].Instances[?State.Name==`running`].[InstanceId,PublicIpAddress,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

### 2. SSH into Instance

```bash
# SSH into your instance
# Replace KEY_FILE with your .pem file path
ssh -i /path/to/key.pem ubuntu@your-instance-ip

# Once connected, verify setup
docker ps
docker-compose ps
```

### 3. Manual Deployment (if needed)

```bash
# On EC2 instance:
cd /opt/oil-spill-app

# Update from repository
git pull origin main

# Restart services
sudo systemctl restart oil-spill-app

# View logs
journalctl -u oil-spill-app -f
```

### 4. Configure Domain/DNS

```bash
# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[?LoadBalancerName==`oil-spill-app-alb`].DNSName' \
  --output text)

echo "Point your domain to: $ALB_DNS"
```

Then in your DNS provider (Route 53, GoDaddy, etc.):
- Create CNAME record: `yourdomain.com` → `<ALB_DNS>`

### 5. Setup HTTPS with ACM

```bash
# Create certificate in AWS Certificate Manager
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names "*.yourdomain.com" \
  --validation-method DNS \
  --region us-east-1

# Validate domain ownership via DNS records
# Then update Terraform with certificate ARN

# In terraform/ec2.tf, uncomment HTTPS listener and add certificate ARN
# Then re-run: terraform apply
```

---

## Monitoring & Maintenance

### 1. CloudWatch Logs

```bash
# View application logs
aws logs tail /aws/ec2/oil-spill-app --follow

# Specific container logs
aws logs tail /aws/ec2/oil-spill-app --log-stream-name-filter "oil_spill" --follow
```

### 2. CloudWatch Metrics

**CPU Utilization:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region us-east-1
```

**RDS Health:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=oil-spill-app-db \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region us-east-1
```

### 2. Database Backups

```bash
# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier oil-spill-app-db \
  --db-snapshot-identifier oil-spill-app-backup-$(date +%Y%m%d) \
  --region us-east-1

# List snapshots
aws rds describe-db-snapshots --region us-east-1 --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime]'
```

### 3. Auto-Scale Configuration

```bash
# Check current ASG status
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names oil-spill-app-asg \
  --region us-east-1

# Update desired capacity
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name oil-spill-app-asg \
  --desired-capacity 3 \
  --region us-east-1
```

### 4. Health Checks

```bash
# Check ALB target health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:ACCOUNT_ID:targetgroup/oil-spill-app-tg/* \
  --region us-east-1

# Test API endpoints
curl -I http://your-alb-dns/health
curl -I http://your-alb-dns/api/detection
```

---

## Troubleshooting

### EC2 Instance Issues

**Instance not starting:**
```bash
# Check instance status
aws ec2 describe-instance-status --instance-ids i-xxxxx --region us-east-1

# Check system log
aws ec2 get-console-output --instance-id i-xxxxx --region us-east-1 | tail -50
```

**Docker not running:**
```bash
# SSH into instance and check
sudo systemctl status docker
sudo systemctl start docker

# Check docker-compose
docker-compose ps
docker-compose logs
```

### Database Connection Issues

```bash
# Test RDS connectivity
mysql -h YOUR_RDS_ENDPOINT -u oil_spill_user -p

# From EC2:
sudo tcpdump -i eth0 -n port 3306  # Monitor connections

# Check security group
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

### Application Errors

```bash
# View application logs
docker-compose logs oil_spill_app -f
docker-compose logs portal_app -f
docker-compose logs realtime_app -f

# Check application health
curl -v http://localhost:5000/health

# Restart container
docker-compose restart oil_spill_app
```

### Out of Disk Space

```bash
# SSH into instance
df -h  # Check disk usage

# Clean up old docker images
docker image prune -a

# Clean up volumes
docker volume prune

# Increase EBS volume size via AWS Console
```

---

## Security Best Practices

### 1. Environment Variables & Secrets

**DO:**
- ✅ Use AWS Secrets Manager for credentials
- ✅ Set file permissions: `chmod 600 .env`
- ✅ Never commit `.env` to git
- ✅ Rotate passwords regularly

**DON'T:**
- ❌ Hardcode passwords in code
- ❌ Commit secrets to repository
- ❌ Share .env files via email
- ❌ Use weak passwords

### 2. Network Security

```bash
# Update security group to restrict SSH
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 22 \
  --cidr YOUR_IP/32 \
  --region us-east-1
```

### 3. SSL/TLS Certificates

```bash
# Generate self-signed cert (for testing)
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes

# Request AWS Certificate Manager (for production)
# See "Setup HTTPS" section above
```

### 4. Database Security

```bash
# Create read-only user
CREATE USER 'readonly'@'10.0.0.0/16' IDENTIFIED BY 'readonly_password';
GRANT SELECT ON oil_spill_db.* TO 'readonly'@'10.0.0.0/16';

# Enable encryption at rest (already in Terraform)
# Enable automated backups
# Enable S3 export
```

### 5. Regular Updates

```bash
# On EC2, enable automatic security updates
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Update Docker images regularly
docker-compose pull
docker-compose up -d
```

---

## Cost Optimization

### 1. Right-sized Instances

**Development:**
```hcl
instance_type = "t3.micro"  # Free tier eligible
db_instance_type = "db.t3.micro"
```

**Production:**
```hcl
instance_type = "t3.medium"
db_instance_type = "db.t3.small"
```

### 2. Stop Unused Resources

```bash
# Stop instances during off-hours
aws ec2 stop-instances --instance-ids i-xxxxx --region us-east-1

# Schedule with EventBridge for automation
```

### 3. S3 Lifecycle Policy

```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket oil-spill-app-uploads \
  --lifecycle-configuration file://lifecycle.json
```

**lifecycle.json:**
```json
{
  "Rules": [
    {
      "ID": "DeleteOldUploads",
      "Status": "Enabled",
      "Prefix": "uploads/",
      "Expiration": { "Days": 90 }
    }
  ]
}
```

---

## Useful Commands Reference

```bash
# Terraform
terraform init              # Initialize
terraform plan             # Plan changes
terraform apply            # Apply changes
terraform destroy          # Destroy infrastructure
terraform refresh          # Refresh state
terraform fmt              # Format code

# Docker
docker-compose up -d       # Start in background
docker-compose down        # Stop all services
docker-compose logs -f     # View logs
docker-compose ps          # List containers
docker exec -it CONTAINER_ID bash  # SSH into container

# AWS CLI
aws ec2 describe-instances               # List instances
aws rds describe-db-instances           # List RDS instances
aws s3 ls                               # List S3 buckets
aws logs tail LOG_GROUP --follow        # Stream logs
aws autoscaling describe-auto-scaling-groups  # Auto scaling status

# Database
mysql -h RDS_ENDPOINT -u USER -p    # Connect to MySQL
mysqldump -h HOST -u USER -p DB_NAME > backup.sql  # Backup

# SSH
ssh -i key.pem ubuntu@INSTANCE_IP
scp -i key.pem -r local/path ubuntu@INSTANCE_IP:/remote/path
```

---

## Support & Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Docker Documentation](https://docs.docker.com/)
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)

---

**Last Updated:** March 1, 2026
**Version:** 1.0
