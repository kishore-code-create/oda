#!/bin/bash
# Production Deployment Script for EC2
# SSH into your EC2 instance and run this script

set -e

APP_DIR="/opt/oil-spill-app"
REPO_URL="https://github.com/your-username/oil-spill-detection.git"

echo "=== Oil Spill Detection - EC2 Production Deployment ==="

# Create app directory
sudo mkdir -p $APP_DIR
cd $APP_DIR

# Clone repository
echo "Cloning repository..."
if [ -d .git ]; then
    git pull origin main
else
    sudo git clone $REPO_URL .
fi

# Update permissions
sudo chown -R ubuntu:ubuntu $APP_DIR

# Create .env file
echo "Creating .env file..."
cat > .env << 'EOF'
FLASK_ENV=production
FLASK_DEBUG=False
DB_HOST=YOUR_RDS_ENDPOINT
DB_USER=oil_spill_user
DB_PASSWORD=YOUR_SECURE_PASSWORD
DB_NAME=oil_spill_db
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
EOF

chmod 600 .env

# Install Docker (if not already installed)
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
fi

# Start services
echo "Starting application..."
sudo docker-compose up -d

# Display status
echo ""
echo "=== Deployment Complete ==="
docker-compose ps
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop services: sudo docker-compose down"
