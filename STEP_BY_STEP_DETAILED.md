# Detailed Step-by-Step Deployment Guide

## Prerequisites (Check Before Starting)

Before beginning, verify you have:

```bash
# 1. AWS Account
- AWS account created
- Logged into AWS Console
- Know your AWS Region (e.g., us-east-1)

# 2. Tools Installed
aws --version                    # AWS CLI v2
terraform --version             # Terraform v1.0+
docker --version               # Docker
docker-compose --version       # Docker Compose
git --version                  # Git

# 3. AWS Credentials
aws configure                  # Should have access keys set

# 4. SSH Key (for EC2 access)
aws ec2 create-key-pair --key-name oil-spill-app-key --region us-east-1 > oil-spill-app-key.pem
chmod 400 oil-spill-app-key.pem
```

**If any tool is missing, install it first:**
- AWS CLI: `pip install awscli`
- Terraform: Download from https://www.terraform.io/downloads.html
- Docker: Download from https://www.docker.com/products/docker-desktop

---

# STEP 1: Configure (.env and terraform.tfvars)

## Part 1A: Create and Configure .env File

### What is .env?
The `.env` file contains sensitive environment variables for your applications:
- Database credentials
- Flask secret key
- AWS access keys
- Google OAuth credentials
- API keys

### Step by Step:

**Step 1: Create .env from template**

```bash
# Navigate to project root
cd "c:\Users\Veeramalla Akshay\OneDrive\Desktop\phase 2"

# Copy the template
cp .env.example .env
```

**Step 2: Open .env in text editor**

```bash
# Windows (PowerShell)
notepad .env

# OR use VS Code
code .env

# OR use nano (Linux/Mac)
nano .env
```

**Step 3: Fill in the values**

Open `.env` and update these values:

```env
# ============ DATABASE ============
# For local testing with Docker:
DB_HOST=mysql                    # Don't change for local docker
DB_PORT=3306
DB_USER=oil_spill_user
DB_PASSWORD=MySecure@Pass123     # CHANGE THIS - make it strong!
                                  # Requirements: mix of Upper/Lower/Numbers/Symbols
                                  # Min 16 characters

# For AWS deployment, this will be replaced by RDS endpoint
# Don't worry about it yet

# ============ FLASK ============
FLASK_ENV=production
FLASK_DEBUG=False

# Generate a secure secret key:
# Python: python -c 'import secrets; print(secrets.token_hex(32))'
# Windows: python -c "import secrets; print(secrets.token_hex(32))"
FLASK_SECRET_KEY=abc123def456ghi789jkl012mno345pqr  # CHANGE THIS
                # Must be 64+ characters (very random)

# ============ AWS CREDENTIALS (optional for local docker) ============
# Get these from AWS IAM console
# AWS Console → IAM → Users → Your User → Security Credentials → Access Keys
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
AWS_S3_BUCKET=oil-spill-app-uploads-YOUR-UNIQUE-ID  # Must be globally unique!

# ============ GOOGLE OAUTH (for Portal app) ============
# Get from: Google Cloud Console → APIs & Services → Credentials
# Only needed if using Portal with Google sign-in
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5001/auth/google/callback  # For local testing

# ============ ROBOFLOW (for ML models) ============
# Get from: Roboflow dashboard → API Keys
ROBOFLOW_API_KEY=your_roboflow_api_key_here

# ============ LOGGING ============
LOG_LEVEL=INFO
LOG_FILE=/var/log/oil-spill-app/app.log

# ============ SECURITY ============
SESSION_COOKIE_SECURE=False      # True for production HTTPS only
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

**Step 4: Save the file**
- Windows: Ctrl+S in notepad/VS Code
- Linux/Mac: Ctrl+X → Y → Enter in nano

**Step 5: Verify it's saved**

```bash
# View your .env file
cat .env

# You should see your values filled in (not xxx placeholders)
```

---

## Part 1B: Create and Configure terraform.tfvars

### What is terraform.tfvars?
This file tells Terraform how to create your AWS infrastructure:
- Instance types (EC2, RDS sizes)
- Number of instances
- Network configuration
- Database credentials for RDS
- S3 bucket name

### Step by Step:

**Step 1: Create terraform.tfvars from template**

```bash
# Navigate to terraform directory
cd terraform

# Copy the template
cp terraform.tfvars.example terraform.tfvars
```

**Step 2: Open in text editor**

```bash
# Windows (PowerShell)
notepad terraform.tfvars

# OR VS Code
code terraform.tfvars

# OR nano
nano terraform.tfvars
```

**Step 3: Fill in your AWS-specific values**

Edit `terraform.tfvars` with REAL values:

```hcl
# AWS Region - where to deploy
# us-east-1 (Virginia), us-west-2 (Oregon), eu-west-1 (Ireland), ap-southeast-1 (Singapore)
aws_region = "us-east-1"

# Application name - used for all resource naming
app_name = "oil-spill-app"

# Environment - dev, staging, prod (used for cost tracking)
environment = "prod"

# EC2 Instance Type - compute power
# Sizes: t3.micro ($10/mo), t3.small ($20/mo), t3.medium ($30/mo), t3.large ($60/mo)
# For TESTING: use t3.micro
# For PRODUCTION: use t3.medium
instance_type = "t3.medium"

# How many EC2 instances to start with
# 1 = single instance (recommended for testing)
# 2+ = high availability
instance_count = 1

# ============ DATABASE CONFIGURATION ============

# RDS Instance Type - database server size
# db.t3.micro ($10/mo), db.t3.small ($50/mo), db.t3.medium ($100/mo)
db_instance_type = "db.t3.small"

# Storage size in GB
# 20GB = $2/month storage cost
# 50GB = $5/month storage cost
db_allocated_storage = 50

# Enable Multi-AZ (Automatic failover across availability zones)
# true = $100+ more per month (production)
# false = save money (development/testing)
db_multi_az = false          # Change to true for production!

# How long to keep automated backups (days)
# 7 days = 1 week
# 30 days = 1 month (production)
db_backup_retention_days = 7

# Database master username (how you'll log in)
# Example: oil_spill_admin
db_username = "oil_spill_user"

# Database password - VERY IMPORTANT!
# Requirements:
#   - Minimum 16 characters
#   - Mix of uppercase, lowercase, numbers, special characters
#   - NO quotes, backslashes, or $ characters
# Example: MySecurePass@123
db_password = "ChangeMe@SecurePass123"

# ============ S3 BUCKET CONFIGURATION ============

# S3 bucket name - MUST be globally unique across ALL AWS accounts
# Examples that are UNIQUE:
#   - oil-spill-app-uploads-12345678
#   - my-org-oil-spill-2025-uniqueid
#   - oil-spill-akshay-uploads
# 
# What works: lowercase letters, numbers, hyphens, dots
# Avoid: spaces, uppercase, special characters (except hyphen, dot)
s3_bucket_name = "oil-spill-app-uploads-your-unique-id"

# ============ SECURITY CONFIGURATION ============

# Which IPs can SSH into your EC2 instances
# Format: ["1.2.3.4/32", "5.6.7.8/32"]
# To find YOUR IP: Run this: curl ifconfig.me
# IMPORTANT: Restrict to ONLY your IP for security
# This is YOUR IP block
ssh_allowed_cidrs = ["0.0.0.0/0"]  # CHANGE THIS TO YOUR IP!
# Example after getting your IP:
# ssh_allowed_cidrs = ["203.0.113.42/32"]  # Only allows 203.0.113.42
```

**Step 4: Get YOUR IP Address**

```bash
# Find your public IP address
curl ifconfig.me

# Or use this in PowerShell:
(Invoke-WebRequest -Uri "https://ifconfig.me").Content

# Example output: 203.0.113.42
# Update terraform.tfvars with: ssh_allowed_cidrs = ["203.0.113.42/32"]
```

**Step 5: Verify S3 bucket name is unique**

```bash
# Test if bucket name exists (it shouldn't)
aws s3api head-bucket --bucket oil-spill-app-uploads-your-unique-id

# If you see "Not Found" or error - bucket name is available ✅
# If you see "404 Not Found" - bucket is available ✅
# If it succeeds - bucket already exists, change the name ❌
```

**Step 6: Save the file**

```bash
# Save in your editor (Ctrl+S)
# Then verify:
cat terraform.tfvars

# You should see all your values filled in
```

### Summary: What You Just Did

| File | Purpose | What to Change |
|------|---------|-----------------|
| `.env` | App secrets | Database password, Flask secret key |
| `terraform.tfvars` | AWS infrastructure | AWS region, instance types, S3 bucket, SSH IP |

---

# STEP 2: Test Locally with Docker

## Why Test Locally?
- Verify everything works BEFORE paying for AWS
- Test faster (no 20-minute infrastructure creation)
- Easier to debug if something breaks
- Free (no AWS costs)

## Part 2A: Prepare for Docker Deployment

**Step 1: Navigate to project root**

```bash
cd "c:\Users\Veeramalla Akshay\OneDrive\Desktop\phase 2"
```

**Step 2: Make deployment script executable**

```bash
# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Linux/Mac
chmod +x scripts/deploy_docker.sh
```

**Step 3: Verify Docker is running**

```bash
# Test Docker
docker --version
docker-compose --version

# If these fail, Docker isn't installed or isn't running
# Windows: Start Docker Desktop application
# Linux/Mac: May need to install
```

## Part 2B: Deploy Locally

**Step 1: Run the deployment script**

```bash
# Windows PowerShell
./scripts/deploy_docker.sh

# Linux/Mac
./scripts/deploy_docker.sh

# The script will:
# 1. Check if .env exists (already created it)
# 2. Generate SSL certificates (self-signed)
# 3. Build Docker images (takes 5-10 minutes first time)
# 4. Start all containers
# 5. Display status
```

**Expected Output:**

```
=== Oil Spill Detection App - Docker Deployment ===
Building Docker images...
[Output from Docker build...]
Starting services...
[Output from docker-compose...]
Checking container status...
NAME              STATUS
mysql            Up 30 seconds (health: starting)
oil_spill_app    Up 20 seconds
portal_app       Up 20 seconds
realtime_app     Up 20 seconds
nginx            Up 10 seconds

Services are running at:
- Oil Spill API: http://localhost:5000
- Portal: http://localhost:5001
- Real Time Detection: http://localhost:5002
- Nginx: https://localhost:443
```

## Part 2C: Test Your Local Deployment

**Step 1: Check if services are running**

```bash
# View all containers
docker-compose ps

# Should show 5 containers all "Up"
```

**Step 2: Test API endpoints**

```bash
# Test Oil Spill API health check
curl -k http://localhost:5000/health

# Should return: {"status": "healthy"}

# Test Portal health check
curl -k http://localhost:5001/health

# Test Real Time health check
curl -k http://localhost:5002/health
```

**Step 3: View application logs**

```bash
# View logs from all services
docker-compose logs --tail 50

# View logs from specific service
docker-compose logs -f oil_spill_app

# View database logs
docker-compose logs -f mysql

# Press Ctrl+C to exit logs
```

**Step 4: Access in browser**

Open in your browser:
- **Oil Spill API:** http://localhost:5000
- **Portal:** http://localhost:5001  
- **Real Time:** http://localhost:5002
- **Nginx (HTTPS):** https://localhost:443

You'll get SSL warning (self-signed cert is OK for testing)

## Part 2D: Verify Everything Works

**Upload a test file (if applicable):**

```bash
# Navigate to http://localhost:5000 in browser
# Look for "Upload" button
# Try uploading a test image
# Check if processing works
```

**Check database:**

```bash
# Connect to MySQL database running in Docker
docker-compose exec mysql mysql -u oil_spill_user -p

# When prompted for password, enter: (your DB_PASSWORD from .env)

# View databases
SHOW DATABASES;

# View tables in oil_spill_db
USE oil_spill_db;
SHOW TABLES;

# Exit MySQL
EXIT;
```

## Part 2E: If Everything Works

Great! You're ready for AWS deployment.

**Keep containers running OR stop them:**

```bash
# Keep running (good for testing)
# Do nothing, they'll keep running

# Stop containers (to save resources)
docker-compose down

# When ready to test again:
docker-compose up -d
```

---

## Part 2F: Troubleshooting Local Deployment

### Problem: "Cannot find docker"
```bash
# Solution: Docker not installed or not in PATH
# Install Docker Desktop from https://www.docker.com
```

### Problem: "Port 5000 already in use"
```bash
# Solution: Kill process using port 5000
# Windows: 
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :5000
kill -9 <PID>
```

### Problem: "Cannot connect to Docker daemon"
```bash
# Solution: Docker not running
# Windows: Start Docker Desktop application
# Linux: sudo systemctl start docker
# Mac: Start Docker app from Applications
```

### Problem: Services won't start
```bash
# Check what went wrong:
docker-compose logs

# View specific service error:
docker-compose logs oil_spill_app

# Try rebuilding:
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Problem: "Database connection failed"
```bash
# Wait for database to be ready
docker-compose logs mysql

# Wait 30 seconds and try again
# Docker waits for mysql to be healthy before starting other services
```

---

# STEP 3: Deploy to AWS

## Prerequisites for AWS Deployment

Before running AWS deployment:

- [ ] `.env` file created and filled
- [ ] `terraform.tfvars` created and filled
- [ ] AWS credentials configured (`aws configure`)
- [ ] Local Docker test passed (recommended)
- [ ] SSH key created (`oil-spill-app-key.pem`)
- [ ] Your IP in `ssh_allowed_cidrs` in terraform.tfvars

## Part 3A: Prepare for AWS Deployment

**Step 1: Verify AWS credentials configured**

```bash
# Test AWS connection
aws sts get-caller-identity

# Should return JSON with your AWS Account ID:
# {
#     "UserId": "AIDAI...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/YourName"
# }

# If error "Unable to locate credentials" - run:
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Default region: us-east-1
# Default output: json
```

**Step 2: Verify Terraform installed**

```bash
terraform --version

# Should show: Terraform v1.x.x
# If not found: Download from https://www.terraform.io/downloads.html
```

**Step 3: Make deployment script executable**

```bash
# Windows
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Linux/Mac
chmod +x scripts/deploy.sh
```

## Part 3B: Run AWS Deployment

**Step 1: Start deployment**

```bash
# Navigate to project root (if not already there)
cd "c:\Users\Veeramalla Akshay\OneDrive\Desktop\phase 2"

# Run deployment script
./scripts/deploy.sh
```

**Step 2: Follow the prompts**

The script will:

```
Step 1: Creating Terraform state bucket...
  - Creates S3 bucket to store infrastructure state
  - Enables versioning and encryption
  - Takes 1-2 minutes

Step 2: Initializing Terraform...
  - Downloads AWS provider
  - Sets up .terraform directory
  - Takes 1-2 minutes

Step 3: Planning infrastructure...
  - terraform plan -out=tfplan
  - Shows what will be created
  - Shows additions, no deletions ✅
  - Takes 2-3 minutes
  - Displays: +50 to add, 0 to change, 0 to destroy

Step 4: Review and confirm
  - Script asks: "Do you want to apply? (yes/no): "
  - Type: yes
  - Press Enter

Step 5: Applying infrastructure (LONGEST STEP)
  - terraform apply tfplan
  - Creates all AWS resources:
    * VPC and subnets
    * RDS database
    * EC2 instances in Auto Scaling Group
    * Load Balancer
    * Security Groups
    * CloudWatch alarms
  - Takes 15-25 minutes
  - Outputs: Created XXX resources

Step 6: Create deployment summary
  - Saves infrastructure details to DEPLOYMENT_INFO.txt
  - Shows important endpoints
```

**Expected Timeline:**

| Step | Duration |
|------|----------|
| State bucket | 1-2 min |
| Terraform init | 1-2 min |
| Terraform plan | 2-3 min |
| Manual review | 1-2 min |
| Terraform apply | 15-25 min |
| **TOTAL** | **20-35 minutes** |

## Part 3C: Monitor Deployment Progress

**In AWS Console:**

```
1. Go to https://console.aws.amazon.com
2. EC2 → Instances
   - Watch EC2 instances being created
   - Status should change from "pending" → "running"

3. RDS → Databases
   - Watch RDS instance being created
   - Status should change from "creating" → "available"

4. S3 → Buckets
   - Watch S3 bucket being created

5. CloudWatch → Log Groups
   - Watch log group being created
   - Logs will start appearing as containers start
```

**In Terminal:**

```bash
# Watch Terraform output
# Script shows progress in real-time

# If you want to see AWS resources as they're created:
aws ec2 describe-instances --query 'Reservations[].Instances[*].[InstanceId, State.Name]' --output table

# Watch RDS creation:
aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier, DBInstanceStatus]' --output table
```

## Part 3D: After Deployment Completes

**Step 1: Check the summary file**

```bash
# View deployment info
cat DEPLOYMENT_INFO.txt

# Or view terraform outputs
cd terraform
terraform output

# Key outputs you'll need:
# - rds_endpoint: oil-spill-app-db.xxxxx.us-east-1.rds.amazonaws.com
# - s3_bucket_name: oil-spill-app-uploads-12345678
# - alb_dns: oil-spill-app-alb-1234567890.us-east-1.elb.amazonaws.com
```

**Step 2: Get your EC2 instance IP**

```bash
# List all instances
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[*].[InstanceId, PublicIpAddress, Tags[?Key==`Name`].Value|[0]]' \
  --output table

# Example output:
# i-0123456789abcdef   203.0.113.42   oil-spill-app-instance
```

**Step 3: SSH into your instance (wait 5 minutes for initialization)**

```bash
# Wait 5 minutes for EC2 to finish initialization
# Then SSH in

# Windows PowerShell:
ssh -i oil-spill-app-key.pem ubuntu@203.0.113.42

# Linux/Mac:
ssh -i oil-spill-app-key.pem ubuntu@203.0.113.42

# First time will ask "Are you sure?"
# Type: yes

# Verify Docker containers are running:
docker-compose ps

# Should show all 5 containers "Up"
```

**Step 4: Configure DNS (if using a domain)**

```bash
# Get ALB DNS name
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[*].[LoadBalancerName, DNSName]' \
  --output table

# Example output:
# oil-spill-app-alb   oil-spill-app-alb-1234567890.us-east-1.elb.amazonaws.com

# In your DNS provider (Route 53, GoDaddy, etc.):
# Create CNAME record:
# Name: yourdomain.com
# Value: oil-spill-app-alb-1234567890.us-east-1.elb.amazonaws.com
# TTL: 300

# Wait 5-15 minutes for DNS to propagate
# Test: ping yourdomain.com
```

**Step 5: Test your application**

```bash
# Test health endpoints
curl https://YOUR_DOMAIN_OR_ALB_DNS/health

# Access in browser
# http://YOUR_DOMAIN_OR_ALB_DNS/
# http://YOUR_DOMAIN_OR_ALB_DNS/portal
# http://YOUR_DOMAIN_OR_ALB_DNS/realtime

# Check logs in CloudWatch
aws logs tail /aws/ec2/oil-spill-app --follow
```

---

## Part 3E: Verify Deployment Success

**Checklist: Everything should be working**

- [ ] Terraform output shows 50+ resources created
- [ ] No errors in Terraform output
- [ ] EC2 instances are "running"
- [ ] RDS database is "available"
- [ ] S3 bucket created
- [ ] Can SSH into EC2 instance
- [ ] `docker-compose ps` shows all containers "Up"
- [ ] Health check endpoints return 200 (success)
- [ ] Can access applications via URL

## Part 3F: Troubleshooting AWS Deployment

### Problem: "Terraform plan shows destroy operations"
```bash
# STOP! Do not run apply!
# This would delete resources

# Solution: Check terraform.tfvars
# Make sure nothing value was accidentally deleted
# Compare with terraform.tfvars.example

# If all values correct:
terraform destroy  # Delete incomplete deployment
# Then start over
```

### Problem: "Access denied" during terraform apply
```bash
# Solution: AWS credentials don't have permission

# Verify user has these IAM policies:
# - EC2FullAccess
# - RDSFullAccess
# - S3FullAccess
# - VPCFullAccess
# - CloudWatchFullAccess

# In AWS Console:
# IAM → Users → Your User → Permissions → Add Policy
```

### Problem: "The S3 bucket already exists"
```bash
# Solution: S3 bucket name not unique

# Choose new unique name:
# oil-spill-app-uploads-nov2025-xyz
# oil-spill-akshay-unique-id

# Update terraform.tfvars:
# s3_bucket_name = "new-unique-name"

# Then re-run:
terraform plan -out=tfplan
terraform apply tfplan
```

### Problem: "EC2 instances not running applications"
```bash
# SSH into instance and check
ssh -i oil-spill-app-key.pem ubuntu@INSTANCE_IP

# Check Docker containers
docker-compose ps

# If containers not running:
docker-compose logs
docker-compose up -d

# Check Cloud logs:
journalctl -u oil-spill-app -f
```

---

# Summary: All 3 Steps

| Step | Duration | What Happens |
|------|----------|--------------|
| **1. Configure** | 10 min | Create .env and terraform.tfvars |
| **2. Test Locally** | 15 min | Deploy with Docker locally, verify works |
| **3. Deploy to AWS** | 25 min | Create AWS infrastructure, deploy app |
| **Total** | **50 minutes** | App live on AWS EC2 |

---

# Quick Command Summary

```bash
# Step 1: Configuration
cp .env.example .env
nano .env                    # Edit .env with your values
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
nano terraform/terraform.tfvars  # Edit with your AWS settings

# Step 2: Local Docker (Optional)
./scripts/deploy_docker.sh   # Deploy locally
docker-compose ps            # Check containers
curl http://localhost:5000/health  # Test API
docker-compose down          # Stop containers

# Step 3: AWS Deployment
./scripts/deploy.sh          # Deploy to AWS
#... Wait 25 minutes ...
aws ec2 describe-instances   # Check instances
ssh -i oil-spill-app-key.pem ubuntu@YOUR_IP  # SSH into instance
curl https://YOUR_DOMAIN/health  # Test deployed app
```

---

# After Deployment: What's Next?

1. **Configure HTTPS:** Create ACM certificate, update load balancer
2. **Configure Domain:** Point DNS to ALB
3. **Monitor:** CloudWatch logs, metrics, alarms
4. **Backup:** Verify RDS automated backups
5. **Security:** Update security groups, enable MFA
6. **Scale:** Adjust Auto Scaling Group settings
7. **Cost:** Monitor AWS billing

See DEPLOYMENT_GUIDE.md for detailed post-deployment steps.

---

**You're ready to deploy! Start with Step 1 above.** 🚀
