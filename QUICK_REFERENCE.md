# AWS Deployment - Quick Reference Card

## One-Time Setup

```bash
# 1. Install prerequisites
# - AWS CLI: pip install awscli
# - Terraform: https://www.terraform.io/downloads.html
# - Docker: https://www.docker.com/products/docker-desktop

# 2. Configure AWS
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output format: json

# 3. Create SSH Key Pair
aws ec2 create-key-pair --key-name oil-spill-app-key --region us-east-1 > oil-spill-app-key.pem
chmod 400 oil-spill-app-key.pem
```

## Local Development

```bash
# Setup
cp .env.example .env
# Edit .env with your configuration

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f oil_spill_app
```

## AWS Deployment

```bash
# 1. Setup Infrastructure
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your settings

# 2. Initialize Terraform
terraform init

# 3. Plan & Review
terraform plan -out=tfplan

# 4. Deploy
terraform apply tfplan

# 5. Get outputs
terraform output
```

## Post-Deployment

```bash
# Get instance IP
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text)

INSTANCE_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "SSH into: ssh -i oil-spill-app-key.pem ubuntu@$INSTANCE_IP"

# Setup domain
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[*].DNSName' \
  --output text)

echo "Point your domain to: $ALB_DNS"
```

## Common Commands

```bash
# View EC2 instances
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`].[InstanceId,PublicIpAddress,Tags]' --output table

# View RDS instances
aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,Endpoint.Address,Engine]' --output table

# View logs
aws logs tail /aws/ec2/oil-spill-app --follow

# Restart application on EC2
ssh -i oil-spill-app-key.pem ubuntu@INSTANCE_IP
sudo systemctl restart oil-spill-app

# Scale up instances
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name oil-spill-app-asg \
  --desired-capacity 3 \
  --region us-east-1

# Create RDS snapshot
aws rds create-db-snapshot \
  --db-instance-identifier oil-spill-app-db \
  --db-snapshot-identifier oil-spill-backup-$(date +%Y%m%d)
```

## Cleanup & Cost Savings

```bash
# Destroy all infrastructure
terraform destroy

# Stop instances without terminating
aws ec2 stop-instances --instance-ids i-xxxxx

# Remove unused resources
docker image prune -a
aws s3 rm s3://bucket-name --recursive
```

## Connection Strings

```bash
# MySQL (RDS)
mysql -h $RDS_ENDPOINT -u oil_spill_user -p

# SSH to EC2
ssh -i oil-spill-app-key.pem ubuntu@$INSTANCE_IP

# API Endpoints
http://your-domain.com/api/detection
http://your-domain.com/portal
http://your-domain.com/realtime
```

## Troubleshooting

```bash
# Check EC2 status
aws ec2 describe-instance-status --instance-ids i-xxxxx

# View EC2 logs
aws ec2 get-console-output --instance-id i-xxxxx

# SSH into instance
ssh -i oil-spill-app-key.pem ubuntu@PUBLIC_IP
sudo docker-compose ps
sudo docker-compose logs

# Check RDS connectivity
mysql -h ENDPOINT -u USER -p -e "SELECT 1"

# View CloudWatch logs
aws logs tail /aws/ec2/oil-spill-app --follow --since 1h

# Check ALB health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...
```

## Important Endpoints

- **Application:** https://your-domain.com
- **API:** https://your-domain.com/api/detection
- **Portal:** https://your-domain.com/portal
- **Real-Time:** https://your-domain.com/realtime
- **AWS Console:** https://console.aws.amazon.com
- **RDS Endpoint:** Check in AWS RDS console

## Environment Variables To Update

```env
FLASK_SECRET_KEY=generate_with_$(python -c 'import secrets; print(secrets.token_hex(32))')
DB_PASSWORD=YOUR_SECURE_PASSWORD
AWS_ACCESS_KEY_ID=YOUR_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
AWS_S3_BUCKET=your-unique-bucket-name
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret
ROBOFLOW_API_KEY=your_api_key
```

## Pricing Reminder

- EC2 t3.medium: ~$30/month
- RDS db.t3.small: ~$50/month
- NAT Gateway: ~$40/month
- Data transfer: ~$20/month
- **Total: ~$150/month** (varies by region)

## Support Resources

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Full documentation
- [README.md](README.md) - Project overview
- [AWS Support](https://console.aws.amazon.com/support/)
- [Terraform Docs](https://www.terraform.io/docs/)
- [Docker Docs](https://docs.docker.com/)
