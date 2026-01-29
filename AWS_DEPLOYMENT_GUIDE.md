# AWS Deployment Guide - Stock Trading Platform

Complete manual step-by-step instructions to deploy on AWS using EC2, DynamoDB, SNS, and IAM roles.

**Note:** This is a manual deployment guide. All steps must be performed manually through the AWS Console or AWS CLI.
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: IAM Setup](#step-1-iam-setup)
4. [Step 2: DynamoDB Setup](#step-2-dynamodb-setup)
5. [Step 3: SNS Setup](#step-3-sns-setup)
6. [Step 4: RDS Setup (Optional)](#step-4-rds-setup-optional)
7. [Step 5: EC2 Setup](#step-5-ec2-setup)
8. [Step 6: Deploy Application](#step-6-deploy-application)
9. [Step 7: Monitoring & Maintenance](#step-7-monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────────┐
│   Users (Web)   │
└────────┬────────┘
         │ HTTPS
         ▼
    ┌─────────────────────────┐
    │   AWS EC2 Instance      │
    │  (Flask Application)    │
    └────┬────────────┬───────┘
         │            │
    ┌────▼─┐  ┌──────▼────┐
    │      │  │           │
    │ SNS  │  │ DynamoDB  │
    │      │  │           │
    └──────┘  └───────────┘
    (Email)      (Data)
```

**Services Used:**
- **EC2**: Application hosting (compute)
- **DynamoDB**: NoSQL database (data storage)
- **SNS**: Notifications (email alerts)
- **IAM**: Authentication & authorization
- **RDS** (Optional): Relational database alternative
- **CloudWatch**: Monitoring & logging
- **Route53** (Optional): Domain management

---

## Prerequisites

✅ AWS Account with billing enabled
✅ AWS CLI installed and configured
✅ Git installed
✅ SSH key pair created
✅ Basic knowledge of AWS services

### Install AWS CLI

**Windows (PowerShell):**
```powershell
# Using Python pip
pip install awscli

# Or download from AWS
# https://aws.amazon.com/cli/
```

**Verify Installation:**
```powershell
aws --version
```

---

## Step 1: IAM Setup

### 1.1 Create IAM Role for EC2

1. Go to **AWS Console** → **IAM** → **Roles**
2. Click **Create role**
3. Select **AWS service** → **EC2**
4. Click **Next**
5. Attach these policies:
   - `AmazonDynamoDBFullAccess`
   - `AmazonSNSFullAccess`
   - `CloudWatchLogsFullAccess`
   - `AWSCodeDeployRoleForEC2` (for auto-deployment)

**Or create custom policy:**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:DeleteItem",
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:*:table/StockTrading*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish",
                "sns:GetTopicAttributes"
            ],
            "Resource": "arn:aws:sns:us-east-1:*:stock-trading-*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:us-east-1:*:*"
        }
    ]
}
```

6. Name the role: `StockTradingEC2Role`
7. Click **Create role**

### 1.2 Create IAM User (Optional - For Local Development)

For local testing, create an IAM user with access keys:

1. Go to **IAM** → **Users** → **Create user**
2. Name: `StockTradingDev`
3. Attach the same policies as the EC2 role
4. Generate access keys (save them securely!)

---

## Step 2: DynamoDB Setup

### 2.1 Create DynamoDB Tables

Run these AWS CLI commands:

```powershell
# Set region
$region = "us-east-1"

# Table 1: Users
aws dynamodb create-table `
  --table-name StockTradingUsers `
  --attribute-definitions AttributeName=username,AttributeType=S `
  --key-schema AttributeName=username,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --region $region

# Table 2: Portfolios
aws dynamodb create-table `
  --table-name StockTradingPortfolios `
  --attribute-definitions AttributeName=username,AttributeType=S `
  --key-schema AttributeName=username,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --region $region

# Table 3: Transactions
aws dynamodb create-table `
  --table-name StockTradingTransactions `
  --attribute-definitions AttributeName=username,AttributeType=S AttributeName=transaction_id,AttributeType=S `
  --key-schema AttributeName=username,KeyType=HASH AttributeName=transaction_id,KeyType=RANGE `
  --billing-mode PAY_PER_REQUEST `
  --region $region

# Table 4: Stocks
aws dynamodb create-table `
  --table-name StockTradingStocks `
  --attribute-definitions AttributeName=symbol,AttributeType=S `
  --key-schema AttributeName=symbol,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --region $region
```

### 2.2 Verify Tables Created

```powershell
aws dynamodb list-tables --region us-east-1
```

Expected output:
```
StockTradingUsers
StockTradingPortfolios
StockTradingTransactions
StockTradingStocks
```

### 2.3 Enable TTL (Optional - for automatic data cleanup)

```powershell
aws dynamodb update-time-to-live `
  --table-name StockTradingTransactions `
  --time-to-live-specification "Enabled=true,AttributeName=expiration_time" `
  --region us-east-1
```

---

## Step 3: SNS Setup

### 3.1 Create SNS Topic

```powershell
aws sns create-topic --name stock-trading-notifications --region us-east-1
```

Save the Topic ARN from output:
```
arn:aws:sns:us-east-1:123456789:stock-trading-notifications
```

### 3.2 Create Email Subscription

```powershell
$topicArn = "arn:aws:sns:us-east-1:123456789:stock-trading-notifications"
$email = "your-email@example.com"

aws sns subscribe `
  --topic-arn $topicArn `
  --protocol email `
  --notification-endpoint $email `
  --region us-east-1
```

**Check email and confirm subscription!**

### 3.3 Add SQS Subscription (Optional - for SMS/Mobile)

```powershell
aws sns set-topic-attributes `
  --topic-arn $topicArn `
  --attribute-name DisplayName `
  --attribute-value "Stock Trading Alerts" `
  --region us-east-1
```

---

## Step 4: RDS Setup (Optional)

Use DynamoDB for simplicity, but if you prefer PostgreSQL:

### 4.1 Create RDS Instance

```powershell
aws rds create-db-instance `
  --db-instance-identifier stock-trading-db `
  --db-instance-class db.t3.micro `
  --engine postgres `
  --master-username admin `
  --master-user-password YourSecurePassword123! `
  --allocated-storage 20 `
  --publicly-accessible `
  --region us-east-1
```

Wait ~5 minutes for instance to be ready.

### 4.2 Get RDS Endpoint

```powershell
aws rds describe-db-instances `
  --db-instance-identifier stock-trading-db `
  --query 'DBInstances[0].Endpoint.Address' `
  --region us-east-1
```

---

## Step 5: EC2 Setup

### 5.1 Create Security Group

```powershell
$groupName = "stock-trading-app"

aws ec2 create-security-group `
  --group-name $groupName `
  --description "Security group for stock trading platform" `
  --region us-east-1

# Get Group ID
$groupId = (aws ec2 describe-security-groups `
  --filters "Name=group-name,Values=$groupName" `
  --region us-east-1 `
  --query 'SecurityGroups[0].GroupId' `
  --output text)

echo "Security Group ID: $groupId"
```

### 5.2 Add Inbound Rules

```powershell
# SSH access (restrict to your IP)
aws ec2 authorize-security-group-ingress `
  --group-id $groupId `
  --protocol tcp `
  --port 22 `
  --cidr 0.0.0.0/0 `
  --region us-east-1

# HTTP access
aws ec2 authorize-security-group-ingress `
  --group-id $groupId `
  --protocol tcp `
  --port 80 `
  --cidr 0.0.0.0/0 `
  --region us-east-1

# HTTPS access
aws ec2 authorize-security-group-ingress `
  --group-id $groupId `
  --protocol tcp `
  --port 443 `
  --cidr 0.0.0.0/0 `
  --region us-east-1

# Flask app (port 5000)
aws ec2 authorize-security-group-ingress `
  --group-id $groupId `
  --protocol tcp `
  --port 5000 `
  --cidr 0.0.0.0/0 `
  --region us-east-1
```

### 5.3 Create Key Pair

```powershell
# Create key pair (only do this once!)
aws ec2 create-key-pair `
  --key-name stock-trading-key `
  --query 'KeyMaterial' `
  --output text `
  --region us-east-1 > stock-trading-key.pem

# Set permissions (Windows)
icacls stock-trading-key.pem /inheritance:r /grant:r "%username%:R"
```

### 5.4 Launch EC2 Instance

```powershell
# Create instance (Ubuntu 22.04 LTS)
aws ec2 run-instances `
  --image-id ami-0c55b159cbfafe1f0 `
  --instance-type t3.micro `
  --key-name stock-trading-key `
  --security-group-ids $groupId `
  --iam-instance-profile Name=StockTradingEC2Role `
  --user-data file://bootstrap.sh `
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=StockTradingApp}]' `
  --region us-east-1

# Get Instance ID
$instanceId = (aws ec2 describe-instances `
  --filters "Name=tag:Name,Values=StockTradingApp" `
  --region us-east-1 `
  --query 'Reservations[0].Instances[0].InstanceId' `
  --output text)

echo "Instance ID: $instanceId"
```

### 5.5 Get Public IP

```powershell
# Wait 30 seconds for instance to start
Start-Sleep -Seconds 30

$publicIp = (aws ec2 describe-instances `
  --instance-ids $instanceId `
  --region us-east-1 `
  --query 'Reservations[0].Instances[0].PublicIpAddress' `
  --output text)

echo "Public IP: $publicIp"
```

---

## Step 6: Deploy Application

### 6.1 Connect to EC2 Instance

```powershell
# On Windows
ssh -i stock-trading-key.pem ec2-user@$publicIp

# Or use PuTTY with the .ppk key
```

### 6.2 Clone Application Repository

```bash
cd /home/ec2-user
git clone https://github.com/yourusername/stock-trading-platform.git
cd stock-trading-platform
```

### 6.3 Create Bootstrap Script

Create `bootstrap.sh` in your project root:

```bash
#!/bin/bash
set -e

# Update system
sudo yum update -y
sudo yum install -y python3-pip git

# Install Python dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create app directory
mkdir -p /opt/stock-trading-app
cd /opt/stock-trading-app

# Clone repository
git clone https://github.com/yourusername/stock-trading-platform.git .

# Create systemd service
sudo tee /etc/systemd/system/stock-trading.service > /dev/null <<EOF
[Unit]
Description=Stock Trading Platform
After=network.target

[Service]
Type=notify
User=ec2-user
WorkingDirectory=/opt/stock-trading-app
Environment="AWS_REGION=us-east-1"
Environment="SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:stock-trading-notifications"
ExecStart=/usr/local/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable stock-trading
sudo systemctl start stock-trading

# Setup CloudWatch logs
pip3 install watchtower
```

### 6.4 Set Environment Variables

```bash
# SSH into instance
ssh -i stock-trading-key.pem ec2-user@$publicIp

# Create .env file
nano /opt/stock-trading-app/.env
```

Add:
```
AWS_REGION=us-east-1
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789:stock-trading-notifications
FLASK_ENV=production
FLASK_SECRET_KEY=your-very-secure-secret-key-here
```

### 6.5 Install Nginx (Reverse Proxy)

```bash
sudo yum install -y nginx

# Create Nginx config
sudo tee /etc/nginx/sites-available/stock-trading > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /opt/stock-trading-app/static/;
        expires 30d;
    }
}
EOF

# Enable Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 6.6 Setup SSL/TLS (Let's Encrypt)

```bash
# Install Certbot
sudo yum install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-domain.com

# Auto-renew
sudo systemctl enable certbot-renew.timer
```

---

## Step 7: Monitoring & Maintenance

### 7.1 CloudWatch Monitoring

```powershell
# Check application logs
aws logs tail /aws/ec2/stock-trading-app --follow --region us-east-1

# Create alarm for high CPU
aws cloudwatch put-metric-alarm `
  --alarm-name stock-trading-high-cpu `
  --alarm-description "Alert when CPU > 80%" `
  --metric-name CPUUtilization `
  --namespace AWS/EC2 `
  --statistic Average `
  --period 300 `
  --threshold 80 `
  --comparison-operator GreaterThanThreshold `
  --evaluation-periods 2 `
  --region us-east-1
```

### 7.2 Check Application Status

```bash
# SSH into instance
ssh -i stock-trading-key.pem ec2-user@$publicIp

# Check service status
sudo systemctl status stock-trading

# View logs
sudo journalctl -u stock-trading -f

# Check DynamoDB connection
python3 -c "from aws import aws_manager; print(aws_manager.health_check())"
```

### 7.3 Auto-Backup DynamoDB

```powershell
# Enable point-in-time recovery
aws dynamodb update-continuous-backups `
  --table-name StockTradingUsers `
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true `
  --region us-east-1
```

### 7.4 Database Scaling

```powershell
# Check current usage
aws cloudwatch get-metric-statistics `
  --namespace AWS/DynamoDB `
  --metric-name ConsumedWriteCapacityUnits `
  --dimensions Name=TableName,Value=StockTradingUsers `
  --start-time (Get-Date).AddHours(-1).ToUniversalTime() `
  --end-time (Get-Date).ToUniversalTime() `
  --period 300 `
  --statistics Sum `
  --region us-east-1
```

---

## Troubleshooting

### Issue: Cannot connect to DynamoDB

**Solution:**
```bash
# Verify IAM role
aws sts get-caller-identity

# Check DynamoDB tables
aws dynamodb list-tables --region us-east-1

# Check security group
aws ec2 describe-security-groups --group-ids $groupId
```

### Issue: SNS notifications not working

**Solution:**
```powershell
# Test SNS
aws sns publish `
  --topic-arn $topicArn `
  --message "Test message" `
  --subject "Test" `
  --region us-east-1

# Check subscriptions
aws sns list-subscriptions-by-topic `
  --topic-arn $topicArn `
  --region us-east-1
```

### Issue: Application won't start

**Solution:**
```bash
# Check logs
sudo journalctl -u stock-trading -n 50

# Test Flask app locally
python3 app.py

# Check port availability
sudo netstat -tlnp | grep 5000
```

### Issue: High DynamoDB costs

**Solution:**
```powershell
# Reduce provisioned capacity (if using PAY_PER_REQUEST)
aws dynamodb update-billing-mode `
  --table-name StockTradingUsers `
  --billing-mode PROVISIONED `
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 `
  --region us-east-1
```

---

## Cost Estimation (Monthly)

| Service | Usage | Cost |
|---------|-------|------|
| EC2 (t3.micro) | 730 hours | $10.00 |
| DynamoDB | On-Demand | $1-5 |
| SNS | 1000 notifications | $0.50 |
| Data Transfer | 10GB out | $0.90 |
| **Total** | | **$12-16/month** |

*Note: AWS Free Tier covers most services for first 12 months*

---

## Next Steps

1. ✅ Complete all AWS setup steps
2. ✅ Deploy application to EC2
3. ✅ Test all features (buy, sell, notifications)
4. ✅ Setup custom domain (optional)
5. ✅ Enable HTTPS with Let's Encrypt
6. ✅ Configure monitoring and alerts
7. ✅ Setup automated backups
8. ✅ Implement scaling policies (auto-scaling groups)

---

## Reference Commands

```powershell
# List all resources
aws ec2 describe-instances --region us-east-1
aws dynamodb list-tables --region us-east-1
aws sns list-topics --region us-east-1

# Delete resources (cleanup)
aws ec2 terminate-instances --instance-ids $instanceId
aws dynamodb delete-table --table-name StockTradingUsers
aws sns delete-topic --topic-arn $topicArn
```

---

For support, check AWS documentation:
- DynamoDB: https://docs.aws.amazon.com/dynamodb/
- EC2: https://docs.aws.amazon.com/ec2/
- SNS: https://docs.aws.amazon.com/sns/
- IAM: https://docs.aws.amazon.com/iam/
