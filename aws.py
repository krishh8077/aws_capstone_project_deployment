
"""
AWS Integration Module for Stock Trading Platform
Handles DynamoDB, SNS, and other AWS services
"""

import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime
import os
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert DynamoDB Decimal to float"""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class AWSConfig:
    """AWS Configuration"""
    
    def __init__(self):
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        self.dynamodb_endpoint = os.environ.get('DYNAMODB_ENDPOINT', None)
        self.sns_topic_arn = os.environ.get('SNS_TOPIC_ARN', '')
        
    def get_dynamodb_resource(self):
        """Get DynamoDB resource"""
        kwargs = {'region_name': self.region}
        if self.dynamodb_endpoint:
            kwargs['endpoint_url'] = self.dynamodb_endpoint
        return boto3.resource('dynamodb', **kwargs)
    
    def get_sns_client(self):
        """Get SNS client"""
        return boto3.client('sns', region_name=self.region)


class DynamoDBHandler:
    """Handle all DynamoDB operations"""
    
    def __init__(self, config):
        self.config = config
        self.dynamodb = config.get_dynamodb_resource()
        self.users_table = self.dynamodb.Table('StockTradingUsers')
        self.portfolios_table = self.dynamodb.Table('StockTradingPortfolios')
        self.transactions_table = self.dynamodb.Table('StockTradingTransactions')
        self.stocks_table = self.dynamodb.Table('StockTradingStocks')
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, username, password_hash):
        """Create new user"""
        try:
            timestamp = datetime.utcnow().isoformat()
            self.users_table.put_item(
                Item={
                    'username': username,
                    'password': password_hash,
                    'balance': Decimal('10000.00'),
                    'created_at': timestamp,
                    'updated_at': timestamp,
                    'is_active': True
                }
            )
            return True
        except ClientError as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user(self, username):
        """Get user by username"""
        try:
            response = self.users_table.get_item(Key={'username': username})
            return response.get('Item', None)
        except ClientError as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user_balance(self, username, new_balance):
        """Update user's cash balance"""
        try:
            self.users_table.update_item(
                Key={'username': username},
                UpdateExpression='SET balance = :b, updated_at = :t',
                ExpressionAttributeValues={
                    ':b': Decimal(str(new_balance)),
                    ':t': datetime.utcnow().isoformat()
                }
            )
            return True
        except ClientError as e:
            print(f"Error updating balance: {e}")
            return False
    
    # ==================== PORTFOLIO OPERATIONS ====================
    
    def get_portfolio(self, username):
        """Get user's portfolio"""
        try:
            response = self.portfolios_table.get_item(Key={'username': username})
            portfolio = response.get('Item', {})
            if 'holdings' not in portfolio:
                portfolio['holdings'] = {}
            return portfolio
        except ClientError as e:
            print(f"Error getting portfolio: {e}")
            return {'username': username, 'holdings': {}}
    
    def update_portfolio(self, username, holdings):
        """Update user's portfolio holdings"""
        try:
            # Convert holdings to DynamoDB-compatible format
            holdings_dict = {}
            for symbol, data in holdings.items():
                holdings_dict[symbol] = {
                    'shares': Decimal(str(data.get('shares', 0))),
                    'avg_price': Decimal(str(data.get('avg_price', 0))),
                    'current_price': Decimal(str(data.get('current_price', 0)))
                }
            
            self.portfolios_table.put_item(
                Item={
                    'username': username,
                    'holdings': holdings_dict,
                    'updated_at': datetime.utcnow().isoformat()
                }
            )
            return True
        except ClientError as e:
            print(f"Error updating portfolio: {e}")
            return False
    
    # ==================== TRANSACTION OPERATIONS ====================
    
    def add_transaction(self, username, transaction_type, symbol, quantity, price, total):
        """Add transaction record"""
        try:
            transaction_id = f"{username}_{symbol}_{datetime.utcnow().timestamp()}"
            
            self.transactions_table.put_item(
                Item={
                    'transaction_id': transaction_id,
                    'username': username,
                    'type': transaction_type,  # BUY or SELL
                    'symbol': symbol,
                    'quantity': Decimal(str(quantity)),
                    'price': Decimal(str(price)),
                    'total': Decimal(str(total)),
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'COMPLETED'
                }
            )
            return transaction_id
        except ClientError as e:
            print(f"Error adding transaction: {e}")
            return None
    
    def get_transactions(self, username, limit=50):
        """Get user's recent transactions"""
        try:
            response = self.transactions_table.query(
                KeyConditionExpression='username = :u',
                ExpressionAttributeValues={':u': username},
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error getting transactions: {e}")
            return []
    
    # ==================== STOCK DATA OPERATIONS ====================
    
    def get_stock_price(self, symbol):
        """Get current stock price"""
        try:
            response = self.stocks_table.get_item(Key={'symbol': symbol})
            stock = response.get('Item', None)
            if stock:
                return {
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'price': float(stock['price']),
                    'change': float(stock['change']),
                    'change_percent': float(stock['change_percent'])
                }
            return None
        except ClientError as e:
            print(f"Error getting stock price: {e}")
            return None
    
    def get_all_stocks(self):
        """Get all available stocks"""
        try:
            response = self.stocks_table.scan()
            stocks = []
            for item in response.get('Items', []):
                stocks.append({
                    'symbol': item['symbol'],
                    'name': item['name'],
                    'price': float(item['price']),
                    'change': float(item['change']),
                    'change_percent': float(item['change_percent'])
                })
            return stocks
        except ClientError as e:
            print(f"Error getting stocks: {e}")
            return []
    
    def update_stock_prices(self, stocks_data):
        """Update stock prices in bulk"""
        try:
            with self.stocks_table.batch_writer() as batch:
                for symbol, data in stocks_data.items():
                    batch.put_item(
                        Item={
                            'symbol': symbol,
                            'name': data['name'],
                            'price': Decimal(str(data['price'])),
                            'change': Decimal(str(data['change'])),
                            'change_percent': Decimal(str(data['change_percent'])),
                            'updated_at': datetime.utcnow().isoformat()
                        }
                    )
            return True
        except ClientError as e:
            print(f"Error updating stocks: {e}")
            return False
    
    def init_stocks_if_needed(self):
        """Initialize stock data if empty"""
        try:
            response = self.stocks_table.scan()
            if response['Count'] == 0:
                stocks_data = {
                    'AAPL': {'name': 'Apple Inc.', 'price': 185.45, 'change': 2.30, 'change_percent': 1.26},
                    'GOOGL': {'name': 'Alphabet Inc.', 'price': 140.25, 'change': -1.75, 'change_percent': -1.23},
                    'MSFT': {'name': 'Microsoft Corp.', 'price': 378.91, 'change': 3.45, 'change_percent': 0.92},
                    'AMZN': {'name': 'Amazon.com Inc.', 'price': 175.85, 'change': -2.10, 'change_percent': -1.18},
                    'TSLA': {'name': 'Tesla Inc.', 'price': 238.47, 'change': 5.62, 'change_percent': 2.41},
                    'META': {'name': 'Meta Platforms Inc.', 'price': 310.28, 'change': 4.13, 'change_percent': 1.35},
                    'NFLX': {'name': 'Netflix Inc.', 'price': 195.63, 'change': -3.28, 'change_percent': -1.65},
                    'NVDA': {'name': 'NVIDIA Corp.', 'price': 875.41, 'change': 12.35, 'change_percent': 1.43}
                }
                self.update_stock_prices(stocks_data)
                return True
            return True
        except ClientError as e:
            print(f"Error initializing stocks: {e}")
            return False


class SNSHandler:
    """Handle SNS notifications"""
    
    def __init__(self, config):
        self.config = config
        self.sns_client = config.get_sns_client()
        self.topic_arn = config.sns_topic_arn
    
    def send_notification(self, email, subject, message):
        """Send SNS notification"""
        if not self.topic_arn:
            print("SNS Topic ARN not configured")
            return False
        
        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message,
                MessageAttributes={
                    'email': {'DataType': 'String', 'StringValue': email}
                }
            )
            print(f"Notification sent. Message ID: {response['MessageId']}")
            return True
        except ClientError as e:
            print(f"Error sending notification: {e}")
            return False
    
    def send_trade_notification(self, username, trade_type, symbol, quantity, price):
        """Send trade execution notification"""
        subject = f"Trade Executed: {trade_type} {quantity} shares of {symbol}"
        message = f"""
Trade Confirmation

User: {username}
Action: {trade_type}
Symbol: {symbol}
Quantity: {quantity} shares
Price: ${price:.2f}
Total: ${float(quantity) * float(price):.2f}

Time: {datetime.utcnow().isoformat()}
        """
        return self.send_notification(username, subject, message)


class AWSManager:
    """Main AWS Manager - Unified interface"""
    
    def __init__(self):
        self.config = AWSConfig()
        self.dynamodb = DynamoDBHandler(self.config)
        self.sns = SNSHandler(self.config)
    
    def initialize(self):
        """Initialize AWS resources"""
        print("Initializing AWS resources...")
        self.dynamodb.init_stocks_if_needed()
        print("AWS resources initialized successfully")
    
    def health_check(self):
        """Check AWS connectivity"""
        try:
            # Try to list tables
            dynamodb = self.config.get_dynamodb_resource()
            tables = dynamodb.tables.all()
            required_tables = ['StockTradingUsers', 'StockTradingPortfolios', 
                             'StockTradingTransactions', 'StockTradingStocks']
            
            existing_tables = [t.name for t in tables]
            missing_tables = [t for t in required_tables if t not in existing_tables]
            
            if missing_tables:
                print(f"Missing tables: {missing_tables}")
                return False
            
            return True
        except Exception as e:
            print(f"Health check failed: {e}")
            return False


# Global AWS Manager instance
aws_manager = AWSManager()

