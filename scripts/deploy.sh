#!/bin/bash
# AWS EC2 Deployment Script
# Run this script to deploy the Oil Spill Detection App to AWS

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Oil Spill Detection App - AWS Deployment ===${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI not found. Install it with: pip install awscli${NC}"
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Terraform not found. Install it from: https://www.terraform.io/downloads.html${NC}"
    exit 1
fi

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}No .env file found. Using defaults.${NC}"
fi

AWS_REGION=${AWS_REGION:-us-east-1}
APP_NAME=${APP_NAME:-oil-spill-app}

echo -e "${GREEN}AWS Region: ${AWS_REGION}${NC}"
echo -e "${GREEN}App Name: ${APP_NAME}${NC}"

# Step 1: Create S3 bucket for Terraform state
echo -e "\n${YELLOW}Step 1: Setting up Terraform state backend...${NC}"
TERRAFORM_STATE_BUCKET="${APP_NAME}-terraform-state-$(date +%s)"
echo "Creating S3 bucket for Terraform state: $TERRAFORM_STATE_BUCKET"

aws s3api create-bucket \
    --bucket "$TERRAFORM_STATE_BUCKET" \
    --region "$AWS_REGION" \
    --create-bucket-configuration LocationConstraint="$AWS_REGION" \
    2>/dev/null || echo "Bucket may already exist"

aws s3api put-bucket-versioning \
    --bucket "$TERRAFORM_STATE_BUCKET" \
    --versioning-configuration Status=Enabled

aws s3api put-bucket-server-side-encryption-configuration \
    --bucket "$TERRAFORM_STATE_BUCKET" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

echo -e "${GREEN}Terraform state bucket created: $TERRAFORM_STATE_BUCKET${NC}"

# Step 2: Initialize Terraform
echo -e "\n${YELLOW}Step 2: Initializing Terraform...${NC}"
cd terraform

# Update backend configuration
cat > backend.tf << EOF
terraform {
  backend "s3" {
    bucket         = "$TERRAFORM_STATE_BUCKET"
    key            = "oil-spill-app/terraform.tfstate"
    region         = "$AWS_REGION"
    encrypt        = true
  }
}
EOF

terraform init

# Step 3: Plan Terraform
echo -e "\n${YELLOW}Step 3: Terraform Plan...${NC}"
terraform plan -out=tfplan

# Step 4: Ask for confirmation
echo -e "\n${YELLOW}Please review the Terraform plan above.${NC}"
read -p "Do you want to apply? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Deployment cancelled.${NC}"
    exit 1
fi

# Step 5: Apply Terraform
echo -e "\n${YELLOW}Step 4: Applying Terraform...${NC}"
terraform apply tfplan

# Step 6: Get outputs
echo -e "\n${GREEN}Step 5: Getting infrastructure details...${NC}"
TERRAFORM_OUTPUTS=$(terraform output -json)
echo "$TERRAFORM_OUTPUTS" > terraform_outputs.json

RDS_ENDPOINT=$(echo "$TERRAFORM_OUTPUTS" | jq -r '.rds_endpoint.value')
ALB_DNS=$(echo "$TERRAFORM_OUTPUTS" | jq -r '.alb_dns.value // empty')
S3_BUCKET=$(echo "$TERRAFORM_OUTPUTS" | jq -r '.s3_bucket_name.value')

cd ..

# Step 7: Create credentials file
echo -e "\n${YELLOW}Step 6: Creating deployment summary...${NC}"
cat > DEPLOYMENT_INFO.txt << EOF
=== Oil Spill Detection App - Deployment Information ===

AWS Region: $AWS_REGION
App Name: $APP_NAME
Terraform State Bucket: $TERRAFORM_STATE_BUCKET

Infrastructure Details:
- RDS Endpoint: $RDS_ENDPOINT
- S3 Bucket: $S3_BUCKET
- ALB DNS: $ALB_DNS

Next Steps:
1. Update your DNS: Point your domain to $ALB_DNS
2. SSH into EC2 instances:
   - Get instance IPs from AWS Console > EC2 > Instances
   - ssh -i your-key.pem ubuntu@<instance-ip>
3. Monitor logs:
   - CloudWatch Logs > /aws/ec2/$APP_NAME
4. Scale your application:
   - Update ASG desired capacity in AWS Console
5. Enable HTTPS:
   - Create ACM certificate
   - Update terraform/ec2.tf with certificate ARN
   - Re-run terraform apply

Deployment completed at: $(date)
EOF

cat DEPLOYMENT_INFO.txt

echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo -e "${YELLOW}Save the following for your records:${NC}"
echo "RDS Endpoint: $RDS_ENDPOINT"
echo "S3 Bucket: $S3_BUCKET"
echo "See DEPLOYMENT_INFO.txt for more details"
