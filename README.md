# 📈 Stock Trading Platform

A user-friendly web application for simulated stock trading, allowing users to practice investing without real money. Perfect for aspiring investors learning to trade stocks.

## 🎯 Features

### Core MVP Features
✅ **User Registration & Authentication**
- Create account with username and password
- Virtual currency allocation ($10,000 starting balance)
- Secure session management

✅ **Stock Search & Discovery**
- Search for stocks by symbol (AAPL, GOOGL, MSFT, etc.)
- Real-time stock price display
- Stock performance indicators (price change %)
- 8 pre-loaded popular stocks

✅ **Buy/Sell Orders**
- Execute buy orders (deduct from balance, add to portfolio)
- Execute sell orders (remove from portfolio, add to balance)
- Real-time order confirmation
- Quantity adjustment with +/- buttons

✅ **Portfolio Management**
- View all holdings with detailed information
- Track average purchase price vs. current price
- Calculate gain/loss per position
- Calculate total portfolio value
- Visual profit/loss indicators

✅ **Trade Confirmation Notifications**
- Order confirmation messages on the UI
- AWS SNS integration ready (optional setup)
- Transaction ID generation for tracking
- Timestamp on all transactions

✅ **Transaction History**
- Complete buy/sell order history
- Sortable and filterable transactions
- Transaction details (symbol, quantity, price, total)
- Status tracking

✅ **Dashboard**
- Account summary (balance, portfolio value, total account value)
- Quick action buttons
- Recent transactions overview
- Holdings snapshot

## 🏗️ Project Structure

```
stock-trading-platform/
├── app.py                          # Flask backend
├── requirements.txt                # Python dependencies
├── templates/
│   ├── base.html                  # Base layout template
│   ├── login.html                 # Login page
│   ├── signup.html                # Registration page
│   ├── dashboard.html             # Main dashboard
│   ├── trade.html                 # Trading interface
│   ├── portfolio.html             # Portfolio view
│   └── transactions.html          # Transaction history
├── static/
│   ├── style.css                  # Complete styling
│   └── script.js                  # Frontend JavaScript
├── trading_data.json              # User data storage (auto-created)
└── README.md                       # This file
```

## 💻 Tech Stack

### Backend
- **Python Flask** - Web framework
- **Flask Session** - User authentication
- **JSON** - Data persistence
- **Boto3** - AWS SNS integration (optional)

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with responsive design
- **Vanilla JavaScript** - Interactivity
- **Font Awesome** - Icons

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone/Download the project**
```bash
cd stock-trading-platform
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Access the application**
Open your browser and navigate to:
```
http://localhost:5000
```

## 📋 Usage Guide

### 1. Create Account
- Click on signup page or navigate to `/signup`
- Enter username and password
- Confirm your password
- You'll receive $10,000 virtual currency to start trading

### 2. Login
- Enter your credentials on the login page
- You'll be redirected to the dashboard

### 3. View Dashboard
- See your account balance, portfolio value, and total account value
- View your current holdings
- See recent transactions

### 4. Trade Stocks
- Navigate to the Trade section
- Search for a stock by symbol (e.g., AAPL)
- Click on a stock to see its details
- Adjust the quantity using +/- buttons
- Click "Buy" to purchase or "Sell" to sell shares

### 5. Monitor Portfolio
- Go to Portfolio section to see all your holdings
- View detailed gain/loss for each position
- See percentage returns

### 6. Check History
- View all your past transactions
- See details like price, quantity, and total amount

## 🔧 Configuration

### Change Secret Key (Production)
In `app.py`, replace:
```python
app.secret_key = 'your-secret-key-change-this-in-production'
```

With a strong random key:
```python
app.secret_key = 'your-very-secure-random-key-here'
```

### Enable AWS SNS Notifications
1. Set up AWS account and SNS topic
2. Install AWS CLI and configure credentials
3. In `app.py`, update:
```python
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:stock-trading-notifications'
SNS_ENABLED = True
```

### Add More Stocks
In `app.py`, add to `STOCK_DATABASE`:
```python
'STOCK_SYMBOL': {'name': 'Company Name', 'price': 123.45, 'change': 2.50}
```

## 📊 Available Stocks

Default stocks included in the platform:
- **AAPL** - Apple Inc.
- **GOOGL** - Alphabet Inc.
- **MSFT** - Microsoft Corp.
- **AMZN** - Amazon.com Inc.
- **TSLA** - Tesla Inc.
- **META** - Meta Platforms
- **NFLX** - Netflix Inc.
- **NVIDIA** - NVIDIA Corp.

## 🔐 Security Considerations

**⚠️ Important: This is a simulation/demo application**

For production deployment:
1. **Hash passwords** - Use werkzeug.security.generate_password_hash()
2. **Use a database** - Replace JSON file storage with PostgreSQL/MySQL
3. **Enable HTTPS** - Use SSL certificates
4. **CSRF Protection** - Implement CSRF tokens
5. **Input Validation** - Sanitize all user inputs
6. **Rate Limiting** - Prevent brute force attacks
7. **Session Security** - Use secure cookies and session management

## 📝 API Endpoints

### Authentication
- `POST /signup` - Create new account
- `POST /login` - User login
- `GET /logout` - User logout

### Dashboard & Portfolio
- `GET /dashboard` - Main dashboard
- `GET /portfolio` - Portfolio view
- `GET /transactions` - Transaction history

### Trading
- `GET /trade` - Trading interface
- `GET /api/stocks` - Get all available stocks
- `GET /api/stock/<symbol>` - Get stock details
- `POST /api/buy` - Execute buy order
- `POST /api/sell` - Execute sell order

## 🎨 Customization

### Change Color Scheme
Edit CSS variables in `static/style.css`:
```css
:root {
    --primary-color: #2563eb;
    --success-color: #10b981;
    --danger-color: #ef4444;
    /* ... */
}
```

### Modify Starting Balance
In `app.py`, change:
```python
'balance': 10000.00,  # Change this value
```

### Update Stock Prices
Modify the `STOCK_DATABASE` dictionary in `app.py` or implement a real-time API connection.

## 📚 Learning Resources

### JavaScript Tips
- `static/script.js` includes utility functions for common tasks
- Form validation, API requests, currency formatting
- Table sorting, search filtering, animations

### Flask Tips
- User data is stored in `trading_data.json`
- Session-based authentication for simplicity
- JSON API endpoints for AJAX requests

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 is busy:
```python
app.run(debug=True, port=5001)  # Change to different port
```

### JSON File Corrupted
Delete `trading_data.json` - it will be recreated when new users register.

### CSS Not Loading
- Clear browser cache (Ctrl+Shift+Delete)
- Check that Flask is serving static files correctly

### Sessions Not Persisting
- Ensure secret key is set
- Check browser cookie settings
- Try clearing cookies and logging in again

## 🚀 Deployment

### Heroku Deployment
1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Add to `requirements.txt`:
```
gunicorn==20.1.0
```

3. Deploy:
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### AWS Deployment
Deploy using AWS Elastic Beanstalk, EC2, or App Runner for production-ready hosting.

## 📞 Support

For issues, questions, or improvements:
1. Check the troubleshooting section
2. Review code comments
3. Test with sample data

## 📄 License

This project is provided as-is for educational purposes.

## 🎓 Learning Objectives

This project demonstrates:
- ✅ Full-stack web development (Python + JavaScript)
- ✅ User authentication and session management
- ✅ RESTful API design
- ✅ Real-time data updates
- ✅ Portfolio management logic
- ✅ Responsive web design
- ✅ Form validation and error handling
- ✅ Data persistence
- ✅ Cloud integration (AWS SNS optional)

## 🎉 Get Started!

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python app.py`
3. Open browser: `http://localhost:5000`
4. Create account and start trading!

---

**Happy Trading! 📊💰**

*Remember: This is a simulated trading platform for educational purposes. Stock prices are static and not real-time.*
