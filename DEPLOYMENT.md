# Stock Trading Platform - Setup & Deployment Guide

## 📋 Table of Contents
1. [Development Setup](#development-setup)
2. [Production Configuration](#production-configuration)
3. [AWS SNS Integration](#aws-sns-integration)
4. [Database Migration](#database-migration)
5. [Security Best Practices](#security-best-practices)
6. [Deployment Options](#deployment-options)

---

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)

### Local Installation

1. **Create project directory**
```bash
mkdir stock-trading-platform
cd stock-trading-platform
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run development server**
```bash
python app.py
```

4. **Access application**
```
http://localhost:5000
```

### Development Mode
The app runs with `debug=True` by default, which means:
- ✅ Auto-reload on code changes
- ✅ Interactive debugger on errors
- ✅ Detailed error pages

---

## Production Configuration

### 1. Change Secret Key

**CRITICAL: Never use the default secret key in production!**

```python
# Generate a secure secret key
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

Output example:
```
jF_x5K-dL_m9N2p7Q_w3R_s6T_v8U_y1
```

Update in `app.py`:
```python
app.secret_key = 'your-generated-secret-key-here'
```

### 2. Disable Debug Mode

```python
# Before
if __name__ == '__main__':
    app.run(debug=True, port=5000)

# After
if __name__ == '__main__':
    app.run(debug=False, port=5000)
```

### 3. Enable HTTPS

Use a reverse proxy like Nginx with SSL certificates.

### 4. Set Environment Variables

```bash
# .env file
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/stocktrading
SNS_ENABLED=True
SNS_TOPIC_ARN=arn:aws:sns:region:account:topic-name
```

---

## AWS SNS Integration

### Prerequisites
- AWS Account
- AWS CLI configured with credentials
- SNS topic created in AWS Console

### Step 1: Create SNS Topic

```bash
aws sns create-topic --name stock-trading-notifications --region us-east-1
```

Output:
```
{
    "TopicArn": "arn:aws:sns:us-east-1:123456789012:stock-trading-notifications"
}
```

### Step 2: Create SNS Subscription

Email subscription:
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:stock-trading-notifications \
  --protocol email \
  --notification-endpoint your-email@example.com
```

SMS subscription:
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:stock-trading-notifications \
  --protocol sms \
  --notification-endpoint +1234567890
```

### Step 3: Update app.py

```python
import boto3

# Configure SNS
sns_client = boto3.client('sns', region_name='us-east-1')
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789012:stock-trading-notifications'
SNS_ENABLED = True  # Set to True when configured

# The send_notification function is already implemented
```

### Step 4: Configure AWS Credentials

```bash
# Option 1: Using AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1

# Option 3: ~/.aws/credentials file
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
region = us-east-1
```

### Testing SNS Integration

```python
# Add to app.py temporarily
@app.route('/test-sns')
def test_sns():
    send_notification('test_user', 'Test Subject', 'Test message')
    return 'SNS notification sent!'

# Visit http://localhost:5000/test-sns
```

---

## Database Migration

### Moving from JSON to PostgreSQL

**Benefits:**
- ✅ Better performance with large user base
- ✅ Concurrent access support
- ✅ Data integrity
- ✅ Easier backups

### Step 1: Install PostgreSQL Driver

```bash
pip install psycopg2-binary sqlalchemy
```

### Step 2: Create Database Models

Create `models.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=10000.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    portfolio = db.relationship('Portfolio', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    avg_price = db.Column(db.Float, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # BUY or SELL
    symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='CONFIRMED')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

### Step 3: Update app.py

```python
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Portfolio, Transaction

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/stocktrading'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
```

---

## Security Best Practices

### 1. Password Hashing

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hashing password on signup
hashed_password = generate_password_hash(password)

# Verifying password on login
if check_password_hash(stored_hash, provided_password):
    # Login successful
```

### 2. Input Validation

```python
from wtforms import StringField, PasswordField, validators
from flask_wtf import FlaskForm

class SignupForm(FlaskForm):
    username = StringField('Username', [
        validators.Length(min=3, max=20),
        validators.Regexp('^[A-Za-z0-9_]+$')
    ])
    password = PasswordField('Password', [
        validators.Length(min=8),
        validators.Regexp(
            '^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]+$',
            message='Password must contain uppercase, lowercase, number, and special char'
        )
    ])
```

### 3. CSRF Protection

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# In templates
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>
```

### 4. SQL Injection Prevention

Use SQLAlchemy ORM (already implemented):
```python
# Safe - uses parameterized queries
user = User.query.filter_by(username=username).first()

# NOT safe - avoid string concatenation
# user = db.session.execute(f"SELECT * FROM user WHERE username = '{username}'")
```

### 5. Rate Limiting

```bash
pip install Flask-Limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/buy', methods=['POST'])
@limiter.limit("5 per minute")
def buy_stock():
    # Limited to 5 requests per minute
```

### 6. HTTPS/SSL

For Nginx:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

### 7. Security Headers

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

---

## Deployment Options

### Option 1: Heroku

1. **Install Heroku CLI**
```bash
# Download from heroku.com/download
```

2. **Create Procfile**
```bash
echo "web: gunicorn app:app" > Procfile
```

3. **Update requirements.txt**
```bash
pip install gunicorn
pip freeze > requirements.txt
```

4. **Deploy**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Option 2: AWS Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize**
```bash
eb init -p python-3.9 stock-trading-app
```

3. **Create environment**
```bash
eb create production
```

4. **Deploy**
```bash
eb deploy
```

### Option 3: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t stock-trading-app .
docker run -p 5000:5000 stock-trading-app
```

### Option 4: Ubuntu Server

1. **SSH into server**
2. **Install dependencies**
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv nginx
```

3. **Clone repository**
```bash
git clone your-repo-url
cd stock-trading-platform
```

4. **Setup virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Setup Nginx as reverse proxy**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **Setup systemd service**

Create `/etc/systemd/system/stock-trading.service`:
```ini
[Unit]
Description=Stock Trading Platform
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/user/stock-trading-platform
ExecStart=/home/user/stock-trading-platform/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable stock-trading
sudo systemctl start stock-trading
```

---

## Monitoring & Logging

### Setup Logging

```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.route('/api/buy', methods=['POST'])
def buy_stock():
    try:
        # ... trade logic
        logger.info(f"User {username} bought {quantity} shares of {symbol}")
    except Exception as e:
        logger.error(f"Trade error: {str(e)}")
```

### Performance Monitoring

```python
from time import time

@app.before_request
def before_request():
    g.start_time = time()

@app.after_request
def after_request(response):
    elapsed = time() - g.start_time
    logger.info(f"{request.method} {request.path} - {elapsed:.2f}s")
    return response
```

---

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL
pg_dump -U user -h localhost stocktrading > backup.sql

# Restore
psql -U user -h localhost stocktrading < backup.sql
```

### JSON Backup

```bash
# Copy trading_data.json to secure location
cp trading_data.json backups/trading_data_$(date +%Y%m%d).json
```

---

## Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| Port already in use | `lsof -i :5000` then `kill -9 PID` |
| Import errors | Ensure all packages in requirements.txt are installed |
| Database connection failed | Check credentials and ensure database is running |
| Static files not loading | Ensure `static/` directory exists and path is correct |
| Cookies not persisting | Check HTTPS/secure cookie settings |

---

For more information, refer to:
- Flask Documentation: https://flask.palletsprojects.com/
- AWS SNS Documentation: https://docs.aws.amazon.com/sns/
- Deployment Guide: See main README.md

