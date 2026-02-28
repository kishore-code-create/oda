# 🚀 VISUAL QUICK START GUIDE

## The 3-Step Deployment in 50 Minutes

```
┌─────────────────────────────────────────────────────────────────┐
│                 STEP 1: CONFIGURE (10 minutes)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1a. Create .env file:                                          │
│      $ cp .env.example .env                                     │
│      $ nano .env                                                │
│                                                                  │
│      Fill in:                                                   │
│      ✎ DB_PASSWORD = MySecure@Pass123                           │
│      ✎ FLASK_SECRET_KEY = (generate: python -c 'import        │
│                              secrets; print(                     │
│                              secrets.token_hex(32))')           │
│      ✎ AWS_S3_BUCKET = oil-spill-app-uploads-UNIQUE-ID         │
│                                                                  │
│  1b. Create terraform.tfvars file:                              │
│      $ cd terraform                                             │
│      $ cp terraform.tfvars.example terraform.tfvars             │
│      $ nano terraform.tfvars                                    │
│                                                                  │
│      Fill in:                                                   │
│      ✎ aws_region = "us-east-1"                                │
│      ✎ instance_type = "t3.medium"                             │
│      ✎ db_password = "ChangeMe@SecurePass123"                  │
│      ✎ s3_bucket_name = "oil-spill-app-uploads-YOUR-ID"       │
│      ✎ ssh_allowed_cidrs = ["YOUR_IP/32"]                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│             STEP 2: TEST LOCALLY (15 minutes)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Run Docker deployment:                                         │
│  $ ./scripts/deploy_docker.sh                                   │
│                                                                  │
│  Wait for all containers to start...                            │
│                                                                  │
│  Verify:                                                        │
│  $ docker-compose ps                                            │
│                                                                  │
│  Should see:                                                    │
│  NAME              STATUS                                       │
│  mysql            Up 30 seconds (health: starting)             │
│  oil_spill_app    Up 20 seconds                                 │
│  portal_app       Up 20 seconds                                 │
│  realtime_app     Up 20 seconds                                 │
│  nginx            Up 10 seconds                                 │
│                                                                  │
│  Test APIs:                                                     │
│  $ curl http://localhost:5000/health                            │
│  $ curl http://localhost:5001/health                            │
│  $ curl http://localhost:5002/health                            │
│                                                                  │
│  Open browser: http://localhost:5000                            │
│                                                                  │
│  When done: $ docker-compose down                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│            STEP 3: DEPLOY TO AWS (25 minutes)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  From project root:                                             │
│  $ ./scripts/deploy.sh                                          │
│                                                                  │
│  Watch progress:                                                │
│  1. S3 bucket created (1-2 min)                                │
│  2. Terraform initialized (1-2 min)                             │
│  3. Infrastructure planned (2-3 min)                            │
│  4. Script asks: "Do you want to apply? (yes/no): "             │
│     ⟹ Type: yes                                                │
│  5. Infrastructure deployed (15-25 min) ← LONGEST STEP          │
│                                                                  │
│  During step 5, Terraform creates:                              │
│  ✓ VPC with 2 subnets                                          │
│  ✓ RDS MySQL database (Multi-AZ)                               │
│  ✓ EC2 instances (1-3)                                         │
│  ✓ Application Load Balancer                                   │
│  ✓ Security groups                                             │
│  ✓ CloudWatch monitoring                                        │
│  ✓ S3 bucket                                                   │
│                                                                  │
│  After completion:                                              │
│  - Check DEPLOYMENT_INFO.txt for endpoints                      │
│  - Get RDS endpoint address                                     │
│  - Get Load Balancer DNS name                                   │
│  - Get EC2 instance IP                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                ↓
                     ✅ DEPLOYMENT COMPLETE!
```

---

## 📝 Configuration Values Cheat Sheet

### What to fill in .env:

```env
DB_PASSWORD=MySecure@Pass123          ← Make this STRONG (16+ chars)
FLASK_SECRET_KEY=abc123def456...      ← Generate: python -c 'import secrets; print(secrets.token_hex(32))'
AWS_S3_BUCKET=oil-spill-uploads-xyz   ← Must be globally UNIQUE
```

**To generate Flask Secret Key:**

Windows PowerShell:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Linux/Mac:
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

This generates: `f4a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1` (paste this as FLASK_SECRET_KEY)

### What to fill in terraform.tfvars:

```hcl
aws_region = "us-east-1"              ← Where to deploy
instance_type = "t3.medium"           ← EC2 size ($30/month)
db_instance_type = "db.t3.small"      ← Database size ($50/month)
db_password = "ChangeMe@SecurePass"   ← Same format as above
s3_bucket_name = "oil-spill-2025-123" ← Create UNIQUE name
ssh_allowed_cidrs = ["YOUR_IP/32"]    ← GET YOUR IP: curl ifconfig.me
```

**To find YOUR IP:**

Windows PowerShell:
```powershell
(Invoke-WebRequest -Uri "https://ifconfig.me").Content
```

Linux/Mac:
```bash
curl ifconfig.me
```

Example output: `203.0.113.42` → Put as `ssh_allowed_cidrs = ["203.0.113.42/32"]`

---

## ⏱️ Timeline Breakdown

```
Step 1: Configure files
├─ Copy .env.example → .env ..................... 2 min
├─ Edit .env (fill 6 values) ................... 3 min
├─ Copy terraform.tfvars.example → terraform.tfvars  2 min
└─ Edit terraform.tfvars (fill 6 values) ....... 3 min
  Subtotal: 10 minutes

Step 2: Test Locally  
├─ Run deploy_docker.sh script ................. 2 min
├─ Build Docker images (first time) ............ 8 min
├─ Start containers ............................ 2 min
├─ Run health checks ........................... 1 min
└─ Stop containers (docker-compose down) ...... 2 min
  Subtotal: 15 minutes

Step 3: Deploy to AWS
├─ Run deploy.sh script ........................ 1 min
├─ Create S3 bucket for state .................. 1 min
├─ Terraform init ............................. 2 min
├─ Terraform plan (review) ..................... 3 min
├─ Review and type 'yes' ....................... 2 min
├─ Terraform apply (LONGEST) ................... 20 min
│ ├─ VPC creation ............................. 2 min
│ ├─ RDS creation ............................ 10 min
│ ├─ EC2 instances ........................... 5 min
│ ├─ Load Balancer ........................... 2 min
│ └─ Security, monitoring setup ............... 1 min
└─ Save outputs ............................... 1 min
  Subtotal: 25 minutes

TOTAL: 50 minutes ⏰
```

---

## ✅ Success Indicators

### After Step 1 (Configure):
- [ ] `.env` file exists with all values filled
- [ ] `terraform/terraform.tfvars` file exists with all values filled
- [ ] No placeholder text (xxx) remaining in either file
- [ ] S3 bucket name is unique (tested with `aws s3api head-bucket`)
- [ ] Password is 16+ characters

### After Step 2 (Test Locally):
- [ ] `docker-compose ps` shows 5 containers all "Up"
- [ ] Health checks respond: `curl http://localhost:5000/health`
- [ ] Can access UI in browser: `http://localhost:5000`
- [ ] No error logs: `docker-compose logs` shows no ERRORs
- [ ] Optional: uploaded file processed successfully

### After Step 3 (Deploy to AWS):
- [ ] `terraform apply` completed with "Applied XXX resources"
- [ ] No errors in Terraform output
- [ ] EC2 instances showing as "running" in AWS Console
- [ ] RDS database showing as "available" in AWS Console
- [ ] S3 bucket created in AWS Console
- [ ] Can SSH into instance: `ssh -i key.pem ubuntu@IP`
- [ ] Docker containers running on instance: `docker-compose ps`

---

## 🐛 Common Mistakes (Don't Do These!)

| ❌ WRONG | ✅ RIGHT | Why |
|---------|---------|-----|
| Leave DB_PASSWORD as placeholder | Change to strong password | Would cause database connection errors |
| Use uppercase in S3 bucket name | Use only lowercase, hyphens | S3 bucket names must be lowercase |
| Don't fill ssh_allowed_cidrs | Set to YOUR IP /32 | SSH won't work from other IPs |
| Commit .env to git | Add to .gitignore | Would expose passwords publicly! |
| Use same password everywhere | Use unique strong passwords | Better security |
| Terraform plan shows destroy → apply | Don't apply! Review first | Could delete existing resources |
| Give all Terraform answers default | Read and change to your values | Would create wrong infrastructure |
| Run docker-compose from wrong folder | Run from project root | Can't find docker-compose.yml |
| Try to deploy before AWS credentials set | Run `aws configure` first | AWS APIs won't work |

---

## 📸 What You'll See (Real Examples)

### Step 2: Docker Deployment Success
```
$ ./scripts/deploy_docker.sh
=== Oil Spill Detection App - Docker Deployment ===
Building Docker images...
[+] Building 487.5s (68/68) FINISHED
[+] Running 5/5
  ✔ mysql Healthy
  ✔ oil_spill_app Started
  ✔ portal_app Started  
  ✔ realtime_app Started
  ✔ nginx Started

=== Deployment Complete ===
NAME              COMMAND          STATUS                  PORTS
mysql            "docker-en..."   Up 43 seconds (health: healthy)  3306/tcp
oil_spill_app    "gunicorn..."    Up 38 seconds (healthy)   0.0.0.0:5000->5000/tcp
portal_app       "gunicorn..."    Up 38 seconds (healthy)   0.0.0.0:5001->5001/tcp
realtime_app     "gunicorn..."    Up 38 seconds (healthy)   0.0.0.0:5002->5002/tcp
nginx            "nginx -g ..."   Up 33 seconds           0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp

Services are running at:
- Oil Spill API: http://localhost:5000
- Portal: http://localhost:5001
- Real Time Detection: http://localhost:5002
- Nginx: https://localhost:443
```

### Step 3: Terraform Deployment Success
```
$ ./scripts/deploy.sh
Step 1: Setting up Terraform state backend...
Creating S3 bucket for Terraform state: oil-spill-app-terraform-state-1704067200
Terraform state bucket created: oil-spill-app-terraform-state-1704067200

Step 2: Initializing Terraform...
Initializing the backend...
Successfully configured the backend "s3"!
Initializing provider plugins...
Terraform has been successfully initialized!

Step 3: Terraform Plan...
Plan: 50 to add, 0 to change, 0 to destroy.

Please review the Terraform plan above.
Do you want to apply? (yes/no): yes

Step 4: Applying Terraform...
aws_vpc.main: Creating...
aws_internet_gateway.main: Creating...
aws_rds_parameter_group.main: Creating...
[... many resources being created ...]
aws_db_instance.mysql: Creating...
aws_autoscaling_group.app: Creating...

Apply complete! Resources: 50 added, 0 changed, 0 destroyed.

Outputs:
rds_endpoint = "oil-spill-app-db.xxxxx.us-east-1.rds.amazonaws.com"
s3_bucket_name = "oil-spill-app-uploads-12345678"
alb_dns = "oil-spill-app-alb-1234567890.us-east-1.elb.amazonaws.com"

=== Deployment Complete ===
```

---

## 💰 Cost Tracking

**What you'll pay per month:**

| Component | Cost | Notes |
|-----------|------|-------|
| EC2 t3.medium | $30 | Can start smaller with t3.micro ($10) |
| RDS db.t3.small | $50 | Includes 20GB storage + backup |
| NAT Gateway | $40 | Allows private EC2 to reach internet |
| Data Transfer | $20 | Outgoing data to internet |
| CloudWatch | $10 | Logs + metrics |
| S3 Storage | $5 | File uploads storage |
| **SUBTOTAL** | **$155** | ~$0.20 per hour |
| **AWS Free Tier** | -$50 | If new account (first 12 months) |
| **YOUR COST** | **~$105** | If new account with free tier |

**Ways to Reduce Cost:**
- Use t3.micro EC2: saves ~$20/month (only for testing)
- Single AZ: saves ~$20/month (no automatic failover)
- Smaller RDS: db.t3.micro saves ~$30/month
- Reserved Instances: saves 30-40% with 1-year commitment
- Stop instances off-hours: saves 50% if not 24/7
- Remove old snapshots: saves storage costs

---

## 🎯 Next Actions After Successful Deployment

1. **Test Application**
   ```bash
   # Get ALB DNS
   aws elbv2 describe-load-balancers --query 'LoadBalancers[*].DNSName' --output text
   
   # Test in browser
   # http://ALB_DNS/
   # http://ALB_DNS/portal
   # http://ALB_DNS/realtime
   ```

2. **Setup HTTPS**
   - Create ACM certificate
   - Attach to ALB
   - Redirect HTTP → HTTPS

3. **Configure Domain**
   - Create CNAME record pointing to ALB DNS
   - Wait for DNS propagation (5-15 min)

4. **Monitor Application**
   ```bash
   # View logs
   aws logs tail /aws/ec2/oil-spill-app --follow
   
   # SSH and check containers
   ssh -i key.pem ubuntu@EC2_IP
   docker-compose ps
   ```

5. **Scale if Needed**
   ```bash
   # Increase instances from 1 to 3
   aws autoscaling set-desired-capacity \
     --auto-scaling-group-name oil-spill-app-asg \
     --desired-capacity 3
   ```

---

## 📞 Quick Help

**Stuck? Check this:**

| Issue | Solution |
|-------|----------|
| "Command not found" | Tool not installed, see prerequisites |
| "Access denied" AWS | Run `aws configure` with correct credentials |
| "Port already in use" | Another app using port 5000, kill it |
| ".env file not found" | Run `cp .env.example .env` |
| "Terraform plan shows destroy" | STOP! Check terraform.tfvars |
| "S3 bucket exists" | Use unique name: `oil-spill-2025-xyz` |
| "Can't SSH into instance" | 1. Wait 5 min for init, 2. Check IP, 3. Check SSH key perms |
| "Containers won't start" | Check `docker-compose logs` for errors |

**More help:**
- See [STEP_BY_STEP_DETAILED.md](STEP_BY_STEP_DETAILED.md) for full instructions
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for post-deployment
- See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for verification

---

## 🎉 You're Ready!

Print this page or open [STEP_BY_STEP_DETAILED.md](STEP_BY_STEP_DETAILED.md) and follow along!

**Happy deploying! 🚀**
