# Pre-Deployment & Post-Deployment Checklists

## Pre-Deployment Checklist (❌ Before Starting)

### Account & Credentials
- [ ] AWS account created
- [ ] IAM user created with programmatic access
- [ ] Access keys downloaded and saved securely
- [ ] Appropriate IAM permissions assigned (EC2, RDS, S3, VPC, CloudWatch)
- [ ] EC2 key pair created and downloaded
- [ ] AWS CLI installed and configured (`aws configure`)

### Local Setup
- [ ] Git repository cloned
- [ ] Python 3.10+ installed
- [ ] Terraform installed (v1.0+)
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] All scripts have executable permissions (`chmod +x scripts/*.sh`)

### Configuration Files
- [ ] `.env.example` reviewed
- [ ] `.env` created from `.env.example`
- [ ] All database credentials set securely
- [ ] Flask secret key generated (`python -c 'import secrets; print(secrets.token_hex(32))'`)
- [ ] AWS credentials added to `.env`
- [ ] Google OAuth credentials obtained (if using portal)
- [ ] Roboflow API key obtained

### Terraform Configuration
- [ ] `terraform/terraform.tfvars.example` reviewed
- [ ] `terraform/terraform.tfvars` created from example
- [ ] `aws_region` set correctly
- [ ] `instance_type` appropriate for workload
- [ ] `db_instance_type` set for expected load
- [ ] `s3_bucket_name` is globally unique
- [ ] `ssh_allowed_cidrs` restricted to your IP
- [ ] Database password strong (min 16 chars, mixed case, numbers, symbols)

### Application Code
- [ ] All hardcoded credentials removed from Python files
- [ ] `config.py` files present in all apps
- [ ] Requirements files up to date
- [ ] Dockerfiles reviewed and correct
- [ ] docker-compose.yml reviewed

### Security Review
- [ ] `.env` and `.tfvars` files in `.gitignore`
- [ ] SSH key file permissions correct (`chmod 400 key.pem`)
- [ ] No credentials committed to git
- [ ] No TODO comments left in deployment scripts
- [ ] SSL certificates ready (self-signed or ACM)

### Testing
- [ ] Docker deployment tested locally (`./scripts/deploy_docker.sh`)
- [ ] All containers started successfully
- [ ] Health checks passing
- [ ] API endpoints responsive
- [ ] Database migrations completed
- [ ] Logs accessible

### Documentation
- [ ] DEPLOYMENT_GUIDE.md read and understood
- [ ] README.md reviewed
- [ ] QUICK_REFERENCE.md bookmarked
- [ ] Team trained on deployment process
- [ ] Runbooks created for common issues

---

## Deployment Execution Checklist

### Step 1: Terraform Initialization
- [ ] `cd terraform`
- [ ] `terraform init` completed successfully
- [ ] No errors in initialization
- [ ] `.terraform/` directory created

### Step 2: Terraform Planning
- [ ] `terraform plan -out=tfplan` reviewed
- [ ] All resources listed as planned
- [ ] No unexpected destroy operations
- [ ] VPC and networking correct
- [ ] RDS configuration verified
- [ ] Security groups properly configured
- [ ] IAM roles and policies correct

### Step 3: Terraform Application
- [ ] Confirmed no destructive changes
- [ ] `terraform apply tfplan` executed
- [ ] All resources created successfully
- [ ] No errors in output
- [ ] `terraform output` saved to file

### Step 4: Infrastructure Verification
- [ ] RDS instance created and available
- [ ] EC2 instances in Auto Scaling Group healthy
- [ ] Load Balancer created and healthy
- [ ] S3 bucket created with correct permissions
- [ ] Security groups applied correctly
- [ ] VPC and subnets configured

### Step 5: Application Deployment
- [ ] EC2 instances passed health checks
- [ ] Docker containers started on instances
- [ ] Application logs show no errors
- [ ] Database tables initialized
- [ ] Jobs/migrations completed successfully
- [ ] API endpoints responding to health checks

### Step 6: Network Configuration
- [ ] Load balancer DNS name noted
- [ ] Domain DNS updated to point to ALB
- [ ] DNS propagation checked
- [ ] HTTPS certificate requested (if not pre-existing)
- [ ] SSL certificate installed on ALB

### Step 7: Monitoring Setup
- [ ] CloudWatch log groups created
- [ ] Log streams showing application logs
- [ ] Metrics dashboard created
- [ ] Alarms configured
- [ ] Email notifications working

---

## Post-Deployment Checklist

### Immediate (First Hour)
- [ ] Access application via public URL
- [ ] Test login/authentication
- [ ] Upload test file and verify processing
- [ ] Check all 3 apps are accessible
- [ ] Verify database connectivity
- [ ] Review CloudWatch logs for errors
- [ ] Test health check endpoints
  ```bash
  curl https://your-domain.com/health
  curl https://your-domain.com/portal/health
  curl https://your-domain.com/realtime/health
  ```

### Day 1
- [ ] Monitor error rates (should be 0%)
- [ ] Check CPU/Memory usage (normal range)
- [ ] Verify log aggregation working
- [ ] Test SSL certificate validity
- [ ] Load test with expected traffic
- [ ] Verify auto-scaling policies trigger appropriately
- [ ] Check backup schedule

### Week 1
- [ ] Review CloudWatch metrics and dashboards
- [ ] Verify log retention policies
- [ ] Check RDS automated backup completion
- [ ] Test database restore procedure
- [ ] Review security group rules
- [ ] Test security with penetration/vulnerability scan
- [ ] Document any issues found
- [ ] Train operations team on monitoring

### Ongoing
- [ ] Daily: Monitor CloudWatch dashboards
- [ ] Weekly: Review logs for warnings/errors
- [ ] Weekly: Check AWS Cost Explorer for unexpected costs
- [ ] Monthly: Review security and update configurations
- [ ] Monthly: Test disaster recovery procedures
- [ ] Quarterly: Security audit and patch updates
- [ ] Quarterly: Performance optimization review

---

## Troubleshooting During Deployment

### Terraform Issues

**Problem:** `Error: access denied`
```bash
# Solution: Check AWS credentials
aws sts get-caller-identity
# Verify IAM policy includes required permissions
```

**Problem:** `Subnet not available for availability zone`
```bash
# Solution: Update availability zones in terraform.tfvars
aws ec2 describe-availability-zones --region YOUR_REGION
```

**Problem:** `S3 bucket already exists`
```bash
# Solution: Use globally unique name
s3_bucket_name = "oil-spill-app-uploads-$(date +%s)"
```

### EC2 Issues

**Problem:** Instances not starting
```bash
# Check instance status
aws ec2 describe-instance-status --instance-ids i-xxxxx
# View system logs
aws ec2 get-console-output --instance-id i-xxxxx | tail -50
```

**Problem:** Can't SSH
```bash
# Verify security group allows SSH from your IP
aws ec2 describe-security-groups --group-ids sg-xxxxx
# Check key pair permissions
chmod 400 your-key.pem
```

### Database Issues

**Problem:** RDS not accessible
```bash
# Verify security group allows port 3306
aws ec2 describe-security-groups --group-ids sg-xxxxx | grep 3306
# Check RDS status
aws rds describe-db-instances --db-instance-identifier oil-spill-app-db
```

**Problem:** Database migration failed
```bash
# SSH into EC2 and check logs
docker-compose logs mysql
# Manually connect and verify
mysql -h RDS_ENDPOINT -u USER -p DB_NAME < database/oil_spill_db.sql
```

### Application Issues

**Problem:** Application containers not starting
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@INSTANCE_IP
# Check logs
docker-compose logs oil_spill_app
# Check environment variables
docker-compose exec oil_spill_app env
```

**Problem:** Health check failing
```bash
# Test endpoint manually
curl -v http://localhost:5000/health
# Verify application running
docker-compose ps
# Check application logs
docker-compose logs -f oil_spill_app
```

---

## Rollback Procedures

### If Deployment Failing

**Option 1: Destroy and Redeploy**
```bash
cd terraform
terraform destroy  # Confirms before destroying
```
Then follow deployment checklist again.

**Option 2: Keep Infrastructure, Redeploy Application**
```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@INSTANCE_IP
# Stop services
sudo docker-compose down
# Pull latest code
git pull origin main
# Restart
sudo docker-compose up -d
```

### If Data Loss Risk

**Before destroying anything:**
```bash
# Backup RDS
aws rds create-db-snapshot \
  --db-instance-identifier oil-spill-app-db \
  --db-snapshot-identifier oil-spill-app-backup-$(date +%Y%m%d-%H%M%S)

# Export S3 data locally
aws s3 sync s3://your-bucket ./local-backup/
```

---

## Post-Failure Recovery

### Step 1: Investigate
- [ ] Check CloudWatch logs for error messages
- [ ] Review AWS Health Dashboard
- [ ] Verify AWS service status
- [ ] Check recent changes/deployments

### Step 2: Prioritize
- [ ] Severity level (critical/high/medium/low)
- [ ] Impact (how many users affected)
- [ ] Mitigation (fastest path to stability)

### Step 3: Mitigate
- [ ] Scale up if performance issue
- [ ] Restart containers if hung
- [ ] Failover RDS if database issue
- [ ] Update DNS if network issue

### Step 4: Remediate
- [ ] Fix underlying issue
- [ ] Deploy fix to production
- [ ] Verify monitoring shows recovery
- [ ] Document root cause

### Step 5: Improve
- [ ] Update runbooks with solution
- [ ] Improve monitoring/alerting
- [ ] Update documentation
- [ ] Train team on prevention

---

## Validation Tests

```bash
# After deployment, run these validation tests:

# 1. API Connectivity
curl -I https://your-domain.com/health

# 2. Database Connectivity
mysql -h RDS_ENDPOINT -u USER -p DB_NAME -e "SELECT COUNT(*) FROM information_schema.tables;"

# 3. S3 Access
aws s3 ls s3://your-bucket/

# 4. Load Balancer Health
aws elbv2 describe-target-health \
  --target-group-arn "arn:aws:elasticloadbalancing:..."

# 5. Auto Scaling
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names oil-spill-app-asg

# 6. Security Group Rules
aws ec2 describe-security-groups --group-ids sg-xxxxx

# 7. CloudWatch Logs
aws logs tail /aws/ec2/oil-spill-app --follow --since 10m

# 8. Application Logs
ssh -i your-key.pem ubuntu@INSTANCE_IP
docker-compose logs --tail 100

# 9. Disk Space
df -h
aws ec2 describe-volumes --volume-ids vol-xxxxx

# 10. Monitoring Alarms
aws cloudwatch describe-alarms --state-value ALARM
```

---

## Emergency Contacts & Escalation

- [ ] AWS Support Plan: (Business/Enterprise/Developer)
- [ ] Escalation contact: _______________
- [ ] On-call engineer: _______________
- [ ] Team lead: _______________
- [ ] Database admin: _______________

---

**Completed By:** _______________ **Date:** _______________ **Time:** _______________
**Approved By:** _______________ **Date:** _______________ **Time:** _______________

---

*Keep a copy of this checklist for each deployment!*
