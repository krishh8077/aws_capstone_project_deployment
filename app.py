from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime
import json
import os
from functools import wraps
import boto3
import uuid

app = Flask(__name__)
# Load secret from environment for production safety
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')

# Toggle using DynamoDB for persistence
USE_DYNAMODB = os.environ.get('USE_DYNAMODB', 'false').lower() == 'true'

# Import AWS manager if DynamoDB mode enabled (aws_manager created in aws.py)
try:
    from aws import aws_manager
except Exception:
    aws_manager = None

# AWS SNS Configuration (optional - set up only if you have AWS credentials)
try:
    sns_client = boto3.client('sns', region_name='us-east-1')
    SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:stock-trading-notifications'
    SNS_ENABLED = False  # Set to True when configured
except:
    SNS_ENABLED = False
    sns_client = None

# Data storage (in production, use a database)
DATA_FILE = 'trading_data.json'


# Simulated stock data
STOCK_DATABASE = {
    'AAPL': {'name': 'Apple Inc.', 'price': 182.45, 'change': 2.35},
    'GOOGL': {'name': 'Alphabet Inc.', 'price': 140.82, 'change': -1.15},
    'MSFT': {'name': 'Microsoft Corp.', 'price': 380.61, 'change': 3.22},
    'AMZN': {'name': 'Amazon.com Inc.', 'price': 181.92, 'change': -0.88},
    'TSLA': {'name': 'Tesla Inc.', 'price': 238.45, 'change': 5.67},
    'META': {'name': 'Meta Platforms', 'price': 485.72, 'change': 8.34},
    'NFLX': {'name': 'Netflix Inc.', 'price': 247.18, 'change': -2.10},
    'NVIDIA': {'name': 'NVIDIA Corp.', 'price': 875.29, 'change': 12.45},
}

def load_data():
    """Load user data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Save user data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def send_notification(username, subject, message):
    """Send SNS notification"""
    if SNS_ENABLED and sns_client:
        try:
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=subject,
                Message=f"User: {username}\n\n{message}"
            )
        except Exception as e:
            print(f"Error sending SNS notification: {e}")

def login_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_user(username):
    """Initialize a new user with default portfolio"""
    if USE_DYNAMODB and aws_manager:
        # Ensure user exists in DynamoDB
        user = aws_manager.dynamodb.get_user(username)
        if not user:
            # create with empty password placeholder; signup should set real password
            aws_manager.dynamodb.create_user(username, '')
            user = aws_manager.dynamodb.get_user(username)
        return user

    data = load_data()
    if username not in data:
        data[username] = {
            'password': '',
            'balance': 10000.00,  # Virtual currency allocation
            'portfolio': {},  # {symbol: {'shares': int, 'avg_price': float}}
            'transactions': [],  # Transaction history
            'created_at': datetime.now().isoformat()
        }
        save_data(data)
    return data[username]

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not password:
            flash('Username and password are required!', 'error')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('signup'))
        
        if USE_DYNAMODB and aws_manager:
            # Check in DynamoDB
            existing = aws_manager.dynamodb.get_user(username)
            if existing:
                flash('Username already exists!', 'error')
                return redirect(url_for('signup'))
            # Note: password should be hashed in production
            aws_manager.dynamodb.create_user(username, password)
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))

        data = load_data()
        if username in data:
            flash('Username already exists!', 'error')
            return redirect(url_for('signup'))
        
        # Create new user
        data[username] = {
            'password': password,  # In production, hash this!
            'balance': 10000.00,
            'portfolio': {},
            'transactions': [],
            'created_at': datetime.now().isoformat()
        }
        save_data(data)
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if USE_DYNAMODB and aws_manager:
            user = aws_manager.dynamodb.get_user(username)
            if user and user.get('password') == password:
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid username or password!', 'error')
            return render_template('login.html')

        data = load_data()
        if username in data and data[username]['password'] == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    username = session['username']
    data = load_data()
    user_data = data.get(username, {})
    
    # Calculate portfolio value
    portfolio_value = 0
    portfolio_details = []
    
    for symbol, holdings in user_data.get('portfolio', {}).items():
        if symbol in STOCK_DATABASE:
            current_price = STOCK_DATABASE[symbol]['price']
            shares = holdings['shares']
            position_value = current_price * shares
            portfolio_value += position_value
            
            portfolio_details.append({
                'symbol': symbol,
                'name': STOCK_DATABASE[symbol]['name'],
                'shares': shares,
                'avg_price': holdings['avg_price'],
                'current_price': current_price,
                'position_value': position_value,
                'gain_loss': position_value - (holdings['avg_price'] * shares)
            })
    
    total_value = user_data.get('balance', 0) + portfolio_value
    
    return render_template('dashboard.html', 
                         username=username,
                         balance=user_data.get('balance', 0),
                         portfolio=portfolio_details,
                         portfolio_value=portfolio_value,
                         total_value=total_value,
                         transactions=user_data.get('transactions', [])[-10:])  # Last 10 transactions

@app.route('/api/stocks')
@login_required
def get_stocks():
    """API endpoint to get available stocks"""
    stocks = []
    for symbol, data in STOCK_DATABASE.items():
        stocks.append({
            'symbol': symbol,
            'name': data['name'],
            'price': data['price'],
            'change': data['change']
        })
    return jsonify(stocks)

@app.route('/trade')
@login_required
def trade():
    """Stock trading interface"""
    return render_template('trade.html', stocks=STOCK_DATABASE)

@app.route('/api/stock/<symbol>')
@login_required
def get_stock_details(symbol):
    """Get details for a specific stock"""
    symbol = symbol.upper()
    if symbol in STOCK_DATABASE:
        stock = STOCK_DATABASE[symbol]
        return jsonify({
            'symbol': symbol,
            'name': stock['name'],
            'price': stock['price'],
            'change': stock['change'],
            'found': True
        })
    return jsonify({'found': False, 'error': 'Stock not found'}), 404

@app.route('/api/stock/<symbol>/history')
@login_required
def get_stock_history(symbol):
    """Get historical price data for a stock with different timeframes"""
    import random
    from datetime import timedelta
    
    symbol = symbol.upper()
    if symbol not in STOCK_DATABASE:
        return jsonify({'error': 'Stock not found'}), 404
    
    # Get timeframe from query parameter (default: 1m for 1 month)
    timeframe = request.args.get('timeframe', '1m')
    
    # Validate timeframe
    if timeframe not in ['5m', '1w', '1m']:
        timeframe = '1m'
    
    current_price = STOCK_DATABASE[symbol]['price']
    base_price = current_price
    labels = []
    prices = []
    
    if timeframe == '5m':
        # 5 minutes: 12 data points (1 hour)
        num_points = 12
        for i in range(num_points, 0, -1):
            minutes = i * 5
            time_str = f"{minutes//60:02d}:{minutes%60:02d}"
            # Very small volatility for intraday (±0.5%)
            price_change = random.uniform(-0.5, 0.5)
            current_price = current_price * (1 + price_change / 100)
            current_price = max(base_price * 0.995, min(current_price, base_price * 1.005))
            prices.append(round(current_price, 2))
            labels.append(time_str)
    
    elif timeframe == '1w':
        # 1 week: 7 daily data points
        num_points = 7
        for i in range(num_points, 0, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%a %m/%d')
            # Moderate volatility (±1%)
            daily_change = random.uniform(-1.0, 1.0)
            current_price = current_price * (1 + daily_change / 100)
            current_price = max(base_price * 0.93, min(current_price, base_price * 1.07))
            prices.append(round(current_price, 2))
            labels.append(date)
    
    else:  # 1m (1 month)
        # 1 month: 30 daily data points
        num_points = 30
        for i in range(num_points, 0, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%m/%d')
            # Standard volatility (±1.5%)
            daily_change = random.uniform(-1.5, 1.5)
            current_price = current_price * (1 + daily_change / 100)
            current_price = max(base_price * 0.85, min(current_price, base_price * 1.15))
            prices.append(round(current_price, 2))
            labels.append(date)
    
    return jsonify({
        'symbol': symbol,
        'labels': labels,
        'prices': prices,
        'current_price': STOCK_DATABASE[symbol]['price'],
        'change': STOCK_DATABASE[symbol]['change']
    })

@app.route('/api/buy', methods=['POST'])
@login_required
def buy_stock():
    """Execute a buy order"""
    username = session['username']
    symbol = request.json.get('symbol', '').upper()
    quantity = int(request.json.get('quantity', 0))

    if symbol not in STOCK_DATABASE:
        return jsonify({'success': False, 'error': 'Stock not found'}), 400

    if quantity <= 0:
        return jsonify({'success': False, 'error': 'Quantity must be positive'}), 400

    stock_price = STOCK_DATABASE[symbol]['price']
    total_cost = stock_price * quantity

    # DynamoDB-backed flow
    if USE_DYNAMODB and aws_manager:
        # Get user and balance
        user = aws_manager.dynamodb.get_user(username) or {}
        balance = float(user.get('balance', 0))

        if total_cost > balance:
            return jsonify({'success': False, 'error': 'Insufficient balance'}), 400

        new_balance = balance - total_cost
        # Update balance in DynamoDB
        aws_manager.dynamodb.update_user_balance(username, new_balance)

        # Update portfolio
        portfolio_item = aws_manager.dynamodb.get_portfolio(username) or {}
        holdings = portfolio_item.get('holdings', {})

        # Normalize holdings (may contain Decimal)
        normalized = {}
        for sym, val in holdings.items():
            normalized[sym] = {
                'shares': int(val.get('shares', 0)),
                'avg_price': float(val.get('avg_price', 0)),
                'current_price': float(val.get('current_price', STOCK_DATABASE.get(sym, {}).get('price', 0)))
            }

        if symbol in normalized:
            old_shares = normalized[symbol]['shares']
            old_avg = normalized[symbol]['avg_price']
            new_shares = old_shares + quantity
            new_avg = (old_avg * old_shares + stock_price * quantity) / new_shares
            normalized[symbol]['shares'] = new_shares
            normalized[symbol]['avg_price'] = new_avg
            normalized[symbol]['current_price'] = stock_price
        else:
            normalized[symbol] = {'shares': quantity, 'avg_price': stock_price, 'current_price': stock_price}

        aws_manager.dynamodb.update_portfolio(username, normalized)

        # Record transaction in DynamoDB
        tx_id = aws_manager.dynamodb.add_transaction(username, 'BUY', symbol, quantity, stock_price, total_cost)

        # Send SNS notification if configured
        try:
            aws_manager.sns.send_trade_notification(username, 'BUY', symbol, quantity, stock_price)
        except Exception:
            pass

        return jsonify({'success': True, 'message': f'Successfully bought {quantity} shares of {symbol}', 'transaction_id': tx_id, 'new_balance': new_balance})

    # Local JSON flow (fallback)
    data = load_data()
    user_data = data[username]

    balance = user_data.get('balance', 0)
    if total_cost > balance:
        return jsonify({'success': False, 'error': 'Insufficient balance'}), 400

    # Update balance
    user_data['balance'] -= total_cost

    # Update portfolio
    if 'portfolio' not in user_data:
        user_data['portfolio'] = {}

    if symbol in user_data['portfolio']:
        old_shares = user_data['portfolio'][symbol]['shares']
        old_avg_price = user_data['portfolio'][symbol]['avg_price']
        new_shares = old_shares + quantity
        new_avg_price = (old_avg_price * old_shares + stock_price * quantity) / new_shares
        user_data['portfolio'][symbol]['shares'] = new_shares
        user_data['portfolio'][symbol]['avg_price'] = new_avg_price
    else:
        user_data['portfolio'][symbol] = {'shares': quantity, 'avg_price': stock_price}

    # Record transaction
    transaction = {
        'id': str(uuid.uuid4()),
        'type': 'BUY',
        'symbol': symbol,
        'quantity': quantity,
        'price': stock_price,
        'total': total_cost,
        'timestamp': datetime.now().isoformat(),
        'status': 'CONFIRMED'
    }
    user_data['transactions'].append(transaction)

    save_data(data)

    # Send notification
    message = f"Buy Order Confirmed!\n\nSymbol: {symbol}\nQuantity: {quantity}\nPrice: ${stock_price}\nTotal: ${total_cost:.2f}"
    send_notification(username, "Stock Purchase Confirmed", message)

    return jsonify({'success': True, 'message': f'Successfully bought {quantity} shares of {symbol}', 'transaction_id': transaction['id'], 'new_balance': user_data['balance']})

@app.route('/api/sell', methods=['POST'])
@login_required
def sell_stock():
    """Execute a sell order"""
    username = session['username']
    symbol = request.json.get('symbol', '').upper()
    quantity = int(request.json.get('quantity', 0))

    if symbol not in STOCK_DATABASE:
        return jsonify({'success': False, 'error': 'Stock not found'}), 400

    if quantity <= 0:
        return jsonify({'success': False, 'error': 'Quantity must be positive'}), 400

    # DynamoDB-backed flow
    if USE_DYNAMODB and aws_manager:
        portfolio_item = aws_manager.dynamodb.get_portfolio(username) or {}
        holdings = portfolio_item.get('holdings', {})

        # Normalize holdings
        normalized = {}
        for sym, val in holdings.items():
            normalized[sym] = {
                'shares': int(val.get('shares', 0)),
                'avg_price': float(val.get('avg_price', 0)),
                'current_price': float(val.get('current_price', STOCK_DATABASE.get(sym, {}).get('price', 0)))
            }

        if symbol not in normalized or normalized[symbol]['shares'] < quantity:
            owned = normalized.get(symbol, {}).get('shares', 0)
            return jsonify({'success': False, 'error': f'Insufficient shares. You own {owned}'}), 400

        stock_price = STOCK_DATABASE[symbol]['price']
        total_proceeds = stock_price * quantity

        # Update balance
        user = aws_manager.dynamodb.get_user(username) or {}
        balance = float(user.get('balance', 0))
        new_balance = balance + total_proceeds
        aws_manager.dynamodb.update_user_balance(username, new_balance)

        # Update holdings
        normalized[symbol]['shares'] -= quantity
        if normalized[symbol]['shares'] == 0:
            del normalized[symbol]

        aws_manager.dynamodb.update_portfolio(username, normalized)

        # Record transaction
        tx_id = aws_manager.dynamodb.add_transaction(username, 'SELL', symbol, quantity, stock_price, total_proceeds)

        try:
            aws_manager.sns.send_trade_notification(username, 'SELL', symbol, quantity, stock_price)
        except Exception:
            pass

        return jsonify({'success': True, 'message': f'Successfully sold {quantity} shares of {symbol}', 'transaction_id': tx_id, 'new_balance': new_balance})

    # Local JSON flow
    data = load_data()
    user_data = data[username]

    if symbol not in user_data.get('portfolio', {}):
        return jsonify({'success': False, 'error': 'You do not own this stock'}), 400

    owned_shares = user_data['portfolio'][symbol]['shares']
    if quantity > owned_shares:
        return jsonify({'success': False, 'error': f'Insufficient shares. You own {owned_shares}'}), 400

    stock_price = STOCK_DATABASE[symbol]['price']
    total_proceeds = stock_price * quantity

    # Update balance
    user_data['balance'] += total_proceeds

    # Update portfolio
    user_data['portfolio'][symbol]['shares'] -= quantity
    if user_data['portfolio'][symbol]['shares'] == 0:
        del user_data['portfolio'][symbol]

    # Record transaction
    transaction = {
        'id': str(uuid.uuid4()),
        'type': 'SELL',
        'symbol': symbol,
        'quantity': quantity,
        'price': stock_price,
        'total': total_proceeds,
        'timestamp': datetime.now().isoformat(),
        'status': 'CONFIRMED'
    }
    user_data['transactions'].append(transaction)

    save_data(data)

    # Send notification
    message = f"Sell Order Confirmed!\n\nSymbol: {symbol}\nQuantity: {quantity}\nPrice: ${stock_price}\nTotal Proceeds: ${total_proceeds:.2f}"
    send_notification(username, "Stock Sale Confirmed", message)

    return jsonify({'success': True, 'message': f'Successfully sold {quantity} shares of {symbol}', 'transaction_id': transaction['id'], 'new_balance': user_data['balance']})

@app.route('/portfolio')
@login_required
def portfolio():
    """Portfolio management page"""
    username = session['username']
    data = load_data()
    user_data = data.get(username, {})
    
    portfolio_details = []
    for symbol, holdings in user_data.get('portfolio', {}).items():
        if symbol in STOCK_DATABASE:
            current_price = STOCK_DATABASE[symbol]['price']
            shares = holdings['shares']
            position_value = current_price * shares
            
            portfolio_details.append({
                'symbol': symbol,
                'name': STOCK_DATABASE[symbol]['name'],
                'shares': shares,
                'avg_price': holdings['avg_price'],
                'current_price': current_price,
                'position_value': position_value,
                'gain_loss': position_value - (holdings['avg_price'] * shares),
                'gain_loss_percent': ((current_price - holdings['avg_price']) / holdings['avg_price'] * 100) if holdings['avg_price'] > 0 else 0
            })
    
    return render_template('portfolio.html', portfolio=portfolio_details)

@app.route('/transactions')
@login_required
def transactions():
    """Transaction history page"""
    username = session['username']
    data = load_data()
    user_data = data.get(username, {})
    
    transactions = user_data.get('transactions', [])
    transactions.reverse()  # Show newest first
    
    return render_template('transactions.html', transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True, port=5000)


