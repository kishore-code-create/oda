# Oil Spill Detection Application - AWS Deployment Package

**Complete Production-Ready Deployment for AWS EC2**

## 📦 What's Included

This package includes everything needed to deploy the Oil Spill Detection application to AWS EC2:

### Infrastructure as Code (Terraform)
- ✅ VPC with public/private subnets across multiple AZs
- ✅ RDS MySQL with Multi-AZ, automated backups
- ✅ EC2 Auto-Scaling Group with health checks
- ✅ Application Load Balancer (ALB) with HTTPS support
- ✅ S3 bucket for uploads with encryption
- ✅ CloudWatch monitoring and alarms
- ✅ Security Groups with least privilege
- ✅ IAM roles with minimal permissions
- ✅ NAT Gateway for private subnet internet access
- ✅ AWS Secrets Manager integration

### Containerization (Docker)
- ✅ Dockerfiles for all 3 applications
- ✅ docker-compose.yml for local development
- ✅ Nginx reverse proxy configuration
- ✅ SSL/TLS support
- ✅ Health checks and auto-restart

### Configuration Management
- ✅ Environment templates (.env.example)
- ✅ Centralized config.py for each app
- ✅ Secrets management with AWS Secrets Manager
- ✅ No hardcoded credentials

### Deployment Automation
- ✅ Automated AWS infrastructure setup (Terraform)
- ✅ Docker-based local deployment
- ✅ EC2 user-data script for automatic setup
- ✅ Production deployment scripts
- ✅ CI/CD ready

### Documentation
- ✅ Comprehensive deployment guide
- ✅ Troubleshooting section
- ✅ Security best practices
- ✅ Monitoring & maintenance guide
- ✅ Cost optimization tips

---

## 🚀 Quick Start

### Option 1: Local Development with Docker

```bash
# 1. Setup environment
cp .env.example .env
nano .env  # Edit configuration

# 2. Deploy locally
chmod +x scripts/deploy_docker.sh
./scripts/deploy_docker.sh

# 3. Access applications
# - Oil Spill API: http://localhost:5000
# - Portal: http://localhost:5001
# - Real Time Detection: http://localhost:5002
# - Nginx: https://localhost:443
```

### Option 2: Full AWS Deployment

```bash
# 1. Install tools
# - AWS CLI v2: https://aws.amazon.com/cli/
# - Terraform: https://www.terraform.io/downloads.html

# 2. Configure AWS credentials
aws configure

# 3. Setup infrastructure
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Edit with your values

terraform init
terraform plan
terraform apply

# 4. Deploy application
chmod +x ../scripts/deploy.sh
../scripts/deploy.sh

# 5. Get outputs
terraform output
```

---

## 📋 File Structure

```
.
├── .env.example                    # Environment template
├── docker-compose.yml              # Docker Compose configuration
├── Dockerfile.oil_spill            # Oil Spill Detection Dockerfile
├── Dockerfile.portal               # Portal App Dockerfile
├── Dockerfile.realtime             # Real Time Detection Dockerfile
├── nginx.conf                      # Nginx reverse proxy config
├── DEPLOYMENT_GUIDE.md             # Comprehensive guide
├── README.md                       # This file
│
├── terraform/
│   ├── main.tf                     # VPC, RDS, S3, IAM setup
│   ├── ec2.tf                      # EC2, ASG, ALB, CloudWatch
│   ├── variables.tf                # Variable definitions
│   ├── outputs.tf                  # Output definitions
│   ├── user_data.sh               # EC2 initialization script
│   ├── terraform.tfvars.example   # Terraform variables template
│   └── backend.tf                  # S3 state backend (auto-generated)
│
├── scripts/
│   ├── deploy.sh                   # AWS infrastructure deployment
│   ├── deploy_docker.sh            # Docker local deployment
│   ├── production_deploy.sh        # Production EC2 deployment
│   └── README.md                   # Scripts documentation
│
├── ODA(OIL)/oil_spill_detection/   # Oil Spill Detection App
│   └── oil_spill_detection/
│       ├── app.py                  # Main Flask app
│       ├── config.py               # Configuration (NEW)
│       ├── requirements.txt        # Python dependencies
│       └── ... (other files)
│
├── OilSpillPortal/                 # Portal Application
│   ├── portal_app.py              # Main Flask app
│   ├── config.py                  # Configuration (NEW)
│   ├── templates/                 # User signup/login
│   └── ... (other files)
│
└── RealTimeDetection/              # Real Time Detection
    ├── app.py                      # Main Flask app
    ├── config.py                   # Configuration (NEW)
    ├── detector.py                 # Detection logic
    └── ... (other files)
```

---

## 🔧 Technologies & Architecture

### Infrastructure
- **Cloud:** AWS (EC2, RDS, S3, VPC, ALB, CloudWatch)
- **IaC:** Terraform
- **Containerization:** Docker & Docker Compose
- **Reverse Proxy:** Nginx
- **Monitoring:** CloudWatch Logs, Metrics, Alarms

### Application Stack
- **Framework:** Flask 2.3
- **Database:** MySQL 8.0 (RDS)
- **ML Framework:** PyTorch
- **Image Processing:** OpenCV
- **API Integration:** Google OAuth, Roboflow

### Deployment
- **Auto Scaling:** EC2 Auto Scaling Group
- **Load Balancing:** Application Load Balancer
- **Health Checks:** ALB + CloudWatch
- **Logging:** CloudWatch Logs

---

## ⚙️ Configuration Reference

### Environment Variables

Create `.env` file from `.env.example`:

```env
# Database (RDS)
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=3306
DB_USER=oil_spill_user
DB_PASSWORD=SECURE_PASSWORD_MIN_16_CHARS

# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=generate_with_secrets.token_hex(32)
FLASK_DEBUG=False

# AWS
AWS_REGION=us-east-1
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name

# Google OAuth (Portal)
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx

# Roboflow (Oil Detection Models)
ROBOFLOW_API_KEY=xxxxx
```

### Terraform Variables

Edit `terraform/terraform.tfvars`:

```hcl
aws_region       = "us-east-1"
app_name         = "oil-spill-app"
environment      = "prod"
instance_type    = "t3.medium"
instance_count   = 1
db_instance_type = "db.t3.small"
db_password      = "VERY_SECURE_PASSWORD"
s3_bucket_name   = "unique-bucket-name"
ssh_allowed_cidrs = ["YOUR_IP/32"]
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Internet Users                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │   AWS Certificate Manager   │
         │        (HTTPS/SSL)          │
         └──────────┬──────────────────┘
                    │
                    ▼
         ┌─────────────────────────┐
         │  Application Load       │
         │     Balancer (ALB)      │
         │   (Health Checks)       │
         └──────────┬──────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │   EC2   │ │   EC2   │ │   EC2   │  (Auto-Scaling)
   │Instance │ │Instance │ │Instance │  (Min 1, Max 3)
   └────┬────┘ └────┬────┘ └────┬────┘
        │           │           │
        └───────────┼───────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   ┌─────────────┐         ┌──────────┐
   │   RDS MySQL │         │ S3 Bucket│
   │  (Multi-AZ) │         │(Uploads) │
   │  Automated  │         │Versioned │
   │  Backups    │         │Encrypted │
   └─────────────┘         └──────────┘
        │
   ┌────────────────────────────────────┐
   │    CloudWatch Logs & Metrics        │
   │    Monitoring & Alarms             │
   └────────────────────────────────────┘
```

---

## 🔒 Security Features

- ✅ **Network Isolation:** VPC with public/private subnets
- ✅ **Database:** RDS Multi-AZ, encryption at rest
- ✅ **Credentials:** AWS Secrets Manager integration
- ✅ **SSL/TLS:** HTTPS with ACM certificates
- ✅ **IAM:** Least privilege access
- ✅ **Firewall:** Security groups restrict traffic
- ✅ **Backups:** Automated RDS snapshots
- ✅ **Logging:** CloudWatch logs for audit trail
- ✅ **Updates:** Automatic security patches
- ✅ **S3:** Bucket encryption, versioning, block public access

---

## 📈 Monitoring & Observability

### CloudWatch Dashboards
- CPU utilization (EC2 & RDS)
- Memory usage
- Disk space
- Network traffic
- Application logs

### Alarms
- High CPU (EC2 & RDS)
- Low disk space
- Unhealthy targets
- Failed deployments

### Logs
- Application logs: `/app/static/logs/`
- Docker logs: `docker-compose logs -f`
- CloudWatch: `/aws/ec2/oil-spill-app`

---

## 💰 Estimated AWS Costs (Monthly)

| Component | Instance Type | Est. Cost |
|-----------|--------------|-----------|
| EC2 | t3.medium (1) | $30 |
| RDS | db.t3.small | $50 |
| NAT Gateway | - | $40 |
| Data Transfer | 100GB | $20 |
| CloudWatch | Logs + Metrics | $10 |
| **Total** | | **~$150** |

*Prices vary by region. Use AWS Cost Calculator for accurate estimates.*

---

## 🆘 Need Help?

1. **Read:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Comprehensive guide
2. **Check:** Troubleshooting section in deployment guide
3. **Logs:** View CloudWatch logs or Docker logs for errors
4. **AWS Console:** Check EC2, RDS, CloudWatch dashboards
5. **Support:** AWS Support (Business/Enterprise plans)

---

## 📝 Pre-Deployment Checklist

- [ ] AWS account created and configured
- [ ] IAM user with EC2, RDS, S3 permissions created
- [ ] EC2 key pair created and downloaded
- [ ] `.env.example` reviewed and customized
- [ ] `terraform.tfvars.example` reviewed and customized
- [ ] Google OAuth credentials obtained (if using portal)
- [ ] Roboflow API key obtained
- [ ] Database credentials secure and unique
- [ ] AWS CLI installed and configured
- [ ] Terraform installed (v1.0+)
- [ ] Docker & Docker Compose installed
- [ ] SSH access tested from your IP

---

## 🚀 Next Steps

1. **Local Testing:** Deploy locally with Docker first
2. **Review Security:** Audit `.env` and security groups
3. **Cost Estimation:** Use AWS Cost Calculator
4. **Deploy to AWS:** Run Terraform scripts
5. **Configure Domain:** Point DNS to ALB
6. **Enable HTTPS:** Create ACM certificate
7. **Monitor:** Set up CloudWatch dashboards
8. **Backup:** Enable automated RDS snapshots
9. **Scale:** Configure auto-scaling policies
10. **Maintain:** Regular updates and patches

---

## 📚 Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [nginx.conf](nginx.conf) - Reverse proxy configuration
- [Terraform Variables](terraform/variables.tf) - Infrastructure options
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [AWS Documentation](https://docs.aws.amazon.com/)

---

## 📄 License & Support

*Deployment package created for Oil Spill Detection Application*

---

**Version:** 1.0  
**Last Updated:** March 1, 2026  
**Status:** Production Ready ✅

---

## 🎯 Key Features Summary

| Feature | Status | Details |
|---------|--------|---------|
| Docker Containerization | ✅ | All 3 apps containerized |
| AWS Terraform | ✅ | Full infrastructure as code |
| Auto-Scaling | ✅ | EC2 ASG with health checks |
| Load Balancing | ✅ | ALB with HTTPS |
| Database Backup | ✅ | Automated RDS snapshots |
| Monitoring | ✅ | CloudWatch logs, metrics, alarms |
| Security | ✅ | Encryption, VPC, IAM, Secrets Manager |
| Secrets Management | ✅ | AWS Secrets Manager integration |
| S3 Integration | ✅ | Encrypted file uploads |
| CI/CD Ready | ✅ | Deployment scripts included |
| Cost Optimized | ✅ | Right-sized instances |
| Documentation | ✅ | Comprehensive guides |

