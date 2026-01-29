# AWS Manual Deployment - Quick Reference

## 📋 Essential Files for Manual Deployment

✅ **aws.py** - AWS integration code (no changes needed)
✅ **AWS_DEPLOYMENT_GUIDE.md** - Complete step-by-step manual instructions  
✅ **requirements.txt** - Updated with AWS dependencies

❌ **DELETED** - deploy-aws.sh (automatic script)
❌ **DELETED** - deploy-aws.ps1 (automatic script)
❌ **DELETED** - AWS_QUICKSTART.md (quick start guide)
❌ **DELETED** - cloudformation-template.yaml (not using CloudFormation)

---

## 🎯 Two Ways to Deploy Manually

### 1️⃣ AWS Console (Most Visual)
**Best for:** Learning AWS, GUI preference
**Time:** ~45 minutes
**Steps:**
- Click-by-click in AWS Console
- No CLI commands needed
- Perfect for beginners

**Follow:** AWS_DEPLOYMENT_GUIDE.md (Step 1-7)

### 2️⃣ AWS CLI Commands (Faster)
**Best for:** Developers, repeatability
**Time:** ~30 minutes
**Steps:**
- Copy-paste AWS CLI commands
- Full control over each resource
- Can save commands as scripts later

**Follow:** AWS_DEPLOYMENT_GUIDE.md (all CLI commands included)

---

## 📖 Getting Started

**Read this file first:**
```
AWS_DEPLOYMENT_GUIDE.md
```

It contains:
- ✅ Architecture overview
- ✅ Prerequisites checklist
- ✅ Step 1: IAM Setup (manual)
- ✅ Step 2: DynamoDB Setup (manual)
- ✅ Step 3: SNS Setup (manual)
- ✅ Step 4: EC2 Setup (manual)
- ✅ Step 5: Deploy Application (manual)
- ✅ Step 6: Monitoring & Maintenance
- ✅ Troubleshooting guide

---

## ⚡ Quick Command Reference

### AWS CLI Prerequisites
```powershell
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Verify setup
aws sts get-caller-identity
```

### DynamoDB Tables (Manual Creation)
```powershell
# Create Users table
aws dynamodb create-table `
  --table-name StockTradingUsers `
  --attribute-definitions AttributeName=username,AttributeType=S `
  --key-schema AttributeName=username,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST

# Create Portfolios table
aws dynamodb create-table `
  --table-name StockTradingPortfolios `
  --attribute-definitions AttributeName=username,AttributeType=S `
  --key-schema AttributeName=username,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST

# Create Transactions table
aws dynamodb create-table `
  --table-name StockTradingTransactions `
  --attribute-definitions AttributeName=username,AttributeType=S AttributeName=transaction_id,AttributeType=S `
  --key-schema AttributeName=username,KeyType=HASH AttributeName=transaction_id,KeyType=RANGE `
  --billing-mode PAY_PER_REQUEST

# Create Stocks table
aws dynamodb create-table `
  --table-name StockTradingStocks `
  --attribute-definitions AttributeName=symbol,AttributeType=S `
  --key-schema AttributeName=symbol,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST

# Verify tables created
aws dynamodb list-tables
```

### SNS Setup (Manual)
```powershell
# Create SNS topic
aws sns create-topic --name stock-trading-notifications

# Subscribe email (replace with your email)
aws sns subscribe `
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:stock-trading-notifications `
  --protocol email `
  --notification-endpoint your-email@example.com

# Note: Confirm subscription in your email!
```

### EC2 Setup (Manual)
```powershell
# Create security group
aws ec2 create-security-group `
  --group-name stock-trading-app `
  --description "Security group for stock trading platform"

# Add ingress rules (SSH, HTTP, HTTPS, Flask)
aws ec2 authorize-security-group-ingress `
  --group-name stock-trading-app `
  --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress `
  --group-name stock-trading-app `
  --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress `
  --group-name stock-trading-app `
  --protocol tcp --port 443 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress `
  --group-name stock-trading-app `
  --protocol tcp --port 5000 --cidr 0.0.0.0/0

# Create key pair (do this once!)
aws ec2 create-key-pair --key-name stock-trading-key > stock-trading-key.pem

# Launch instance
aws ec2 run-instances `
  --image-id ami-0c55b159cbfafe1f0 `
  --instance-type t3.micro `
  --key-name stock-trading-key `
  --security-group-names stock-trading-app `
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=StockTradingApp}]'

# Get instance IP
aws ec2 describe-instances `
  --filters "Name=tag:Name,Values=StockTradingApp" `
  --query 'Reservations[0].Instances[0].PublicIpAddress'
```

### Application Deployment (Manual via SSH)
```bash
# SSH into instance (use your key)
ssh -i stock-trading-key.pem ubuntu@YOUR_INSTANCE_IP

# Update system
sudo apt-get update
sudo apt-get install -y python3-pip git nginx

# Clone repository
git clone https://github.com/YOUR_USERNAME/stock-trading-platform.git
cd stock-trading-platform

# Install dependencies
pip3 install -r requirements.txt

# Create .env file with your settings
nano .env
# Add:
# AWS_REGION=us-east-1
# SNS_TOPIC_ARN=your-topic-arn
# FLASK_SECRET_KEY=your-secret-key

# Run application
python3 app.py
# Or use gunicorn:
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

---

## 📊 Cost Monitoring (Manual)

```powershell
# View DynamoDB usage
aws cloudwatch get-metric-statistics `
  --namespace AWS/DynamoDB `
  --metric-name ConsumedReadCapacityUnits `
  --dimensions Name=TableName,Value=StockTradingUsers `
  --start-time (Get-Date).AddHours(-1).ToUniversalTime() `
  --end-time (Get-Date).ToUniversalTime() `
  --period 300 `
  --statistics Sum

# View EC2 CPU usage
aws cloudwatch get-metric-statistics `
  --namespace AWS/EC2 `
  --metric-name CPUUtilization `
  --dimensions Name=InstanceId,Value=YOUR_INSTANCE_ID `
  --start-time (Get-Date).AddHours(-1).ToUniversalTime() `
  --end-time (Get-Date).ToUniversalTime() `
  --period 300 `
  --statistics Average
```

---

## 🧹 Cleanup (Manual)

When done, delete resources to avoid costs:

```powershell
# Delete EC2 instance
aws ec2 terminate-instances --instance-ids YOUR_INSTANCE_ID

# Delete DynamoDB tables
aws dynamodb delete-table --table-name StockTradingUsers
aws dynamodb delete-table --table-name StockTradingPortfolios
aws dynamodb delete-table --table-name StockTradingTransactions
aws dynamodb delete-table --table-name StockTradingStocks

# Delete SNS topic
aws sns delete-topic --topic-arn YOUR_TOPIC_ARN

# Delete security group
aws ec2 delete-security-group --group-name stock-trading-app

# Delete IAM role
aws iam delete-role --role-name StockTradingEC2Role
```

---

## 📞 Support

- **AWS Documentation:** https://docs.aws.amazon.com/
- **DynamoDB Guide:** https://docs.aws.amazon.com/dynamodb/
- **EC2 Guide:** https://docs.aws.amazon.com/ec2/
- **SNS Guide:** https://docs.aws.amazon.com/sns/
- **Full Guide:** See AWS_DEPLOYMENT_GUIDE.md

---

## ✅ Deployment Checklist

- [ ] Read AWS_DEPLOYMENT_GUIDE.md
- [ ] AWS CLI installed and configured
- [ ] EC2 key pair created
- [ ] Email ready for SNS
- [ ] Create IAM role (Step 1)
- [ ] Create DynamoDB tables (Step 2)
- [ ] Create SNS topic (Step 3)
- [ ] Launch EC2 instance (Step 4)
- [ ] Deploy application (Step 5)
- [ ] Test application
- [ ] Monitor and maintain

**You control every step manually!**
