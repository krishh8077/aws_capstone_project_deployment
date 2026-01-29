# Installation & Setup Instructions

## 🎯 Complete Step-by-Step Guide

This guide will walk you through installing and running the Stock Trading Platform from scratch.

---

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 2GB (recommended 4GB+)
- **Storage**: 200MB for installation
- **Browser**: Modern browser (Chrome, Firefox, Safari, Edge)

---

## Installation Steps

### Step 1: Check Python Installation

Open terminal/command prompt and verify Python is installed:

```bash
python --version
```

**Expected output:** `Python 3.8.x` or higher

If Python is not installed:
- **Windows**: Download from python.org and run installer
- **macOS**: Use Homebrew: `brew install python3`
- **Linux**: `sudo apt-get install python3 python3-pip`

### Step 2: Navigate to Project Directory

```bash
cd path/to/stock-trading-platform
```

### Step 3: Create Virtual Environment (Optional but Recommended)

**Why?** Isolates project dependencies from system Python

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Required Packages

Install all dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

**What gets installed:**
- Flask 2.3.3 - Web framework
- Werkzeug 2.3.7 - WSGI server
- Boto3 3.28.0 - AWS SDK
- Botocore 1.31.0 - AWS API

**Installation time:** ~30-60 seconds

### Step 5: Verify Installation

Verify all packages installed correctly:

```bash
pip list
```

Should show:
```
Flask                2.3.3
Werkzeug             2.3.7
boto3                1.28.0
botocore             1.31.0
```

### Step 6: Run the Application

Start the Flask development server:

```bash
python app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
 * Restarting with reloader
 * Debugger is active!
```

### Step 7: Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

You should see the Stock Trading Platform landing page! 🎉

---

## First Run Checklist

- [ ] Python installed (version 3.8+)
- [ ] pip working correctly
- [ ] Project directory contains all files
- [ ] Virtual environment created (optional)
- [ ] Dependencies installed successfully
- [ ] No errors when running `python app.py`
- [ ] Browser opens to http://localhost:5000
- [ ] Landing page displays correctly

---

## Creating Your First Account

1. **Click** "Get Started - Free" button
2. **Enter** username (e.g., `testuser`)
3. **Enter** password (minimum 6 characters)
4. **Confirm** password
5. **Click** "Sign Up"
6. **Redirected** to login page
7. **Enter** credentials and click "Login"
8. **Welcome!** You're on the dashboard with $10,000 virtual currency

---

## Making Your First Trade

1. **Click** "Buy/Sell Stocks" or navigate to Trade page
2. **Search** for a stock (e.g., type "AAPL")
3. **Click** on Apple Inc. from the list
4. **Adjust** quantity to 10 shares using +/- buttons
5. **Click** green "Buy" button
6. **See** confirmation: "✓ Successfully bought 10 shares of AAPL"
7. **Go** to Portfolio to see your new position
8. **Great!** Your first trade is complete!

---

## File Structure Overview

After running the project, your directory will look like:

```
stock-trading-platform/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── trading_data.json        # User data (created on first signup)
│
├── templates/               # HTML templates folder
│   ├── base.html           # Layout template
│   ├── index.html          # Landing page
│   ├── login.html          # Login form
│   ├── signup.html         # Registration form
│   ├── dashboard.html      # Main dashboard
│   ├── trade.html          # Trading interface
│   ├── portfolio.html      # Portfolio view
│   └── transactions.html   # Transaction history
│
├── static/                  # Static files folder
│   ├── style.css           # CSS styling
│   └── script.js           # JavaScript code
│
└── Documentation Files
    ├── README.md           # Main documentation
    ├── QUICKSTART.md       # Quick start guide
    ├── DEPLOYMENT.md       # Production setup
    └── FEATURES.md         # Complete features list
```

---

## Troubleshooting Installation

### Issue: "Python is not recognized"

**Problem:** Python command not found in terminal

**Solutions:**
1. Ensure Python is added to PATH
2. On Windows, reinstall Python and check "Add Python to PATH"
3. Restart terminal after installation
4. Use `python3` instead of `python`

### Issue: "No module named 'flask'"

**Problem:** Flask not installed

**Solutions:**
```bash
# Make sure requirements.txt is in current directory
pip install -r requirements.txt

# Or install manually
pip install Flask==2.3.3
```

### Issue: "Address already in use"

**Problem:** Port 5000 is already in use

**Solutions:**
```bash
# Option 1: Kill process using port 5000
# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -i :5000
kill -9 <PID>

# Option 2: Change port in app.py
# Change: app.run(debug=True, port=5000)
# To:     app.run(debug=True, port=5001)
```

### Issue: "Module not found" error

**Problem:** A required module is missing

**Solutions:**
```bash
# Reinstall all requirements
pip install --force-reinstall -r requirements.txt

# Or install specific module
pip install -r requirements.txt --no-cache-dir
```

### Issue: Static files not loading (CSS/JS not working)

**Problem:** Styling or JavaScript not applied

**Solutions:**
1. Refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Check that `static/` folder exists with style.css and script.js
4. Restart Flask server

### Issue: "trading_data.json" errors

**Problem:** User data file corrupted or missing

**Solutions:**
```bash
# Delete the file (it will be recreated)
rm trading_data.json

# Or if on Windows:
del trading_data.json

# Create new account to regenerate
```

---

## Customization After Installation

### Change Application Port

In `app.py`, find the last line:

```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Change port number:
```python
app.run(debug=True, port=8080)  # Use port 8080 instead
```

### Change Application Title

In `templates/base.html`, change:
```html
<span>StockTrade</span>
```

To your preferred name:
```html
<span>My Trading App</span>
```

### Change Starting Balance

In `app.py`, find in `init_user()` function:
```python
'balance': 10000.00,
```

Change to desired amount:
```python
'balance': 50000.00,  # Start with $50,000
```

---

## Regular Maintenance

### Clean Up User Data

Reset all users (WARNING: Deletes all accounts and trades):

```bash
# Delete the data file
rm trading_data.json

# On Windows:
del trading_data.json

# File will be recreated on next signup
```

### Backup User Data

```bash
# Create backup
cp trading_data.json trading_data_backup_$(date +%Y%m%d).json

# Or on Windows:
copy trading_data.json trading_data_backup.json
```

### Update Dependencies

```bash
# Check for updates
pip list --outdated

# Update all packages
pip install --upgrade -r requirements.txt
```

---

## Optional: Setup with Virtual Environment (Recommended)

Virtual environments isolate project dependencies.

### Windows Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Deactivate when done
deactivate
```

### macOS/Linux Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Deactivate when done
deactivate
```

---

## Optional: AWS SNS Setup (Notifications)

### Prerequisites
- AWS Account (free tier available)
- AWS CLI installed
- AWS credentials configured

### Steps

1. **Create SNS Topic**
```bash
aws sns create-topic --name stock-trading-notifications --region us-east-1
```

2. **Note the TopicArn** from the output

3. **Update app.py**
```python
SNS_TOPIC_ARN = 'your-arn-here'
SNS_ENABLED = True
```

4. **Configure AWS Credentials**
```bash
aws configure
```

5. **Restart Application**
```bash
python app.py
```

---

## Next Steps After Installation

1. ✅ **Verify Installation** - Make sure everything runs
2. ✅ **Create Account** - Test user registration
3. ✅ **Make First Trade** - Test trading functionality
4. ✅ **Explore Features** - Navigate through all pages
5. ✅ **Review Code** - Understand the structure
6. ✅ **Read Documentation** - Check QUICKSTART.md
7. ✅ **Customize** - Make it your own!

---

## Getting Help

If you encounter issues:

1. **Check Troubleshooting Section** - Above in this document
2. **Review QUICKSTART.md** - Common issues
3. **Check DEPLOYMENT.md** - Production setup
4. **Read README.md** - Full documentation
5. **Check Browser Console** - F12 to see errors
6. **Check Terminal Output** - Flask error messages

---

## System Requirements Verification

Run this script to verify your system:

```bash
# Check Python
python --version

# Check pip
pip --version

# Check internet connection
ping google.com

# Verify disk space
df -h   # macOS/Linux
dir     # Windows
```

---

## Uninstallation / Cleanup

To completely remove the application:

### Option 1: Keep project folder
```bash
# Just remove Python packages
pip uninstall -r requirements.txt -y

# Deactivate virtual environment
deactivate

# Remove virtual environment folder
rm -rf venv  # macOS/Linux
rmdir venv   # Windows
```

### Option 2: Remove everything
```bash
# Remove entire project folder
rm -rf stock-trading-platform  # macOS/Linux
rmdir /s stock-trading-platform  # Windows
```

---

## Performance Tips

- **Faster Loading**: Clear browser cache before starting
- **Better Performance**: Use Chrome or Firefox (most optimized)
- **Stable Connection**: Run on local network if possible
- **Resource Usage**: Close other applications while developing
- **Data Backup**: Regularly backup trading_data.json

---

## Security Reminder

⚠️ **Important for Production:**
- Change the secret key in app.py
- Add password hashing (Werkzeug)
- Enable HTTPS
- Add input validation
- Use a real database (PostgreSQL)
- Review DEPLOYMENT.md for security guidelines

---

## Support Resources

- **Python Documentation**: https://docs.python.org/3/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Project Guides**: README.md, QUICKSTART.md, DEPLOYMENT.md

---

## Quick Reference Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Create virtual environment
python -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Activate virtual environment (Windows)
venv\Scripts\activate

# Deactivate virtual environment
deactivate

# List installed packages
pip list

# Upgrade pip
pip install --upgrade pip
```

---

## 🎉 You're All Set!

Your Stock Trading Platform is now installed and ready to use!

**Next Steps:**
1. Run: `python app.py`
2. Open: `http://localhost:5000`
3. Create an account
4. Start trading! 📊💰

For detailed guides, see README.md, QUICKSTART.md, DEPLOYMENT.md, and FEATURES.md in your project directory.

---

*Installation guide completed. Happy trading!* 🚀
