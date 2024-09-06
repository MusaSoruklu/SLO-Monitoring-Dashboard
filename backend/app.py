from datetime import datetime
from flask import Flask, jsonify, request, Response
import yfinance as yf
import pandas as pd
import requests
from prometheus_client import start_http_server, Summary, Counter, Gauge, generate_latest
from flask_cors import CORS
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from flask_sqlalchemy import SQLAlchemy
import os
import psutil

app = Flask(__name__)
CORS(app)  # Allow all domains on all routes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market_news.db'  # Example for SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'Total number of requests')
REQUEST_LATENCY = Summary('request_latency_seconds', 'Time spent processing request')
ERROR_COUNT = Counter('error_count', 'Total number of errors')
SUCCESS_COUNT = Counter('success_count', 'Total number of successful requests')
TICKER_REQUEST_COUNT = Counter('ticker_request_count', 'Number of requests per ticker', ['ticker'])
# Define Counters for each HTTP status code range
HTTP_RESPONSES_INFO = Counter('http_responses_info', '1xx Informational responses')
HTTP_RESPONSES_SUCCESS = Counter('http_responses_success', '2xx Successful responses')
HTTP_RESPONSES_REDIRECTION = Counter('http_responses_redirection', '3xx Redirection messages')
HTTP_RESPONSES_CLIENT_ERROR = Counter('http_responses_client_error', '4xx Client error responses')
HTTP_RESPONSES_SERVER_ERROR = Counter('http_responses_server_error', '5xx Server error responses')

# Custom metrics
MEMORY_RSS = Gauge('memory_rss_bytes', 'Resident Set Size Memory Usage')
MEMORY_VMS = Gauge('memory_vms_bytes', 'Virtual Memory Size Usage')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU Usage Percent')

api_key = 'TJ59HNMX6SLPB9TQ'
ts = TimeSeries(key=api_key)
fd = FundamentalData(key=api_key)

# Start a Prometheus metrics server on port 8000
start_http_server(8000)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, default=db.func.now())
    tickers = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<News {self.title}>'
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=2000000)  # Initialize with £2,000,000

    def __repr__(self):
        return f'<User {self.username}>'
    
class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Ensure foreign key is pointing to 'user.id'
    user = db.relationship('User', backref=db.backref('portfolios', lazy=True))  # Set up relationship
    ticker = db.Column(db.String(10), nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f'<Portfolio {self.ticker}>'
    
@app.cli.command('init-db')
def init_db_command():
    """Drops existing tables, recreates them, and seeds with default data."""
    db.drop_all()  # Drop all tables
    db.create_all()  # Create all necessary tables based on the model definitions
    print('All tables dropped and recreated.')

    # Creating and checking for default user
    default_user = User.query.filter_by(username='admin').first()
    if not default_user:
        # Creating the default admin user with a specified balance
        default_user = User(username='admin', password='admin', balance=2000000)  # Initializing with £2,000,000
        db.session.add(default_user)
        db.session.commit()
        print('Added default admin user with initial balance of £2,000,000.')

    # Check and add sample news entries
    if News.query.count() == 0:
        news_samples = [
            {"title": "Tesla Surpasses Market Expectations", "content": "Tesla's latest earnings report shows a surprising increase in profits, surpassing Wall Street predictions.", "tickers": "TSLA", "posted_on": datetime(2024, 8, 30, 14, 30)},
            {"title": "Apple Unveils New Product Line", "content": "Apple has announced a new line of innovative products scheduled to be released next quarter.", "tickers": "AAPL", "posted_on": datetime(2024, 8, 30, 15, 0)},
            {"title": "Amazon Expands to New Markets", "content": "Amazon declares its expansion into new international markets, aiming to double its global footprint.", "tickers": "AMZN", "posted_on": datetime(2024, 8, 30, 16, 0)},
            {"title": "Microsoft Acquires AI Startup", "content": "Microsoft has acquired an AI startup to enhance its cloud computing capabilities.", "tickers": "MSFT", "posted_on": datetime(2024, 8, 30, 17, 0)},
            {"title": "Google Faces Antitrust Investigation", "content": "Google is under scrutiny as new antitrust investigations seek to explore its business practices.", "tickers": "GOOGL", "posted_on": datetime(2024, 8, 30, 18, 0)}
        ]
        for news in news_samples:
            new_news = News(title=news['title'], content=news['content'], tickers=news['tickers'], posted_on=news['posted_on'])
            db.session.add(new_news)
        db.session.commit()
        print('Added sample news stories to the database.')

    # Seed the portfolio if not already present
    portfolio_data = [
        {'ticker': 'AAPL', 'purchase_price': 150.0, 'shares': 2000},
        {'ticker': 'MSFT', 'purchase_price': 250.0, 'shares': 1200},
        {'ticker': 'GOOGL', 'purchase_price': 2800.0, 'shares': 340},
        {'ticker': 'AMZN', 'purchase_price': 3100.0, 'shares': 300},
        {'ticker': 'FB', 'purchase_price': 270.0, 'shares': 1500},
        {'ticker': 'TSLA', 'purchase_price': 800.0, 'shares': 1250},
        {'ticker': 'NFLX', 'purchase_price': 500.0, 'shares': 800},
        {'ticker': 'INTC', 'purchase_price': 50.0, 'shares': 5000},
        {'ticker': 'CSCO', 'purchase_price': 45.0, 'shares': 2200},
        {'ticker': 'ORCL', 'purchase_price': 60.0, 'shares': 1700},
        {'ticker': 'IBM', 'purchase_price': 130.0, 'shares': 900},
        {'ticker': 'NVDA', 'purchase_price': 500.0, 'shares': 800},
        {'ticker': 'PYPL', 'purchase_price': 180.0, 'shares': 1100},
        {'ticker': 'ADBE', 'purchase_price': 470.0, 'shares': 600},
        {'ticker': 'BABA', 'purchase_price': 220.0, 'shares': 1400}
    ]
    for entry in portfolio_data:
        new_stock = Portfolio(ticker=entry['ticker'], purchase_price=entry['purchase_price'], shares=entry['shares'], user_id=default_user.id)  # Set user_id to the default user's id
        db.session.add(new_stock)
    db.session.commit()
    print('Completed database initialization with all sample data.')

@app.route('/metrics', methods=['GET'])
def metrics():
    # Return the metrics in a format that Prometheus expects.
    content = generate_latest()  # Fetch all the metrics in Prometheus' text format
    headers = {'Content-Type': 'text/plain; charset=utf-8'}  # Ensure correct headers for Prometheus scraping
    return Response(content, mimetype="text/plain")


def update_system_metrics():
    process = os.getpid()

    # Attempt to get memory usage for linux
    try:
        if os.name == 'posix':  # Unix-like system
            # Use `/proc` filesystem to get memory usage on Linux
            with open(f'/proc/{process}/status') as f:
                lines = f.readlines()
                for line in lines:
                    if 'VmRSS:' in line:
                        rss = int(line.split()[1]) * 1024  # Convert KB to Bytes
                        MEMORY_RSS.set(rss)
                    elif 'VmSize:' in line:
                        vms = int(line.split()[1]) * 1024  # Convert KB to Bytes
                        MEMORY_VMS.set(vms)
          # For Windows
        elif os.name == 'nt':
            process = psutil.Process(process)
            rss = process.memory_info().rss  # In bytes
            vms = process.memory_info().vms  # In bytes
            MEMORY_RSS.set(rss)
            MEMORY_VMS.set(vms)
                        
    except Exception as e:
        print(f"Error fetching memory info: {e}")

    # Get CPU usage, simpler method
    try:
        cpu_usage = os.getloadavg()[0] * 100  # Simple example using load average on Unix
        CPU_USAGE.set(cpu_usage)
    except Exception as e:
        print(f"Error fetching CPU usage: {e}")


# After request function to track status codes
@app.after_request
def track_status_codes(response):
    # Get the status code from the response
    status_code = response.status_code
    
    # Increment the appropriate counter based on the status code range
    if 100 <= status_code < 200:
        HTTP_RESPONSES_INFO.inc()
    elif 200 <= status_code < 300:
        HTTP_RESPONSES_SUCCESS.inc()
    elif 300 <= status_code < 400:
        HTTP_RESPONSES_REDIRECTION.inc()
    elif 400 <= status_code < 500:
        HTTP_RESPONSES_CLIENT_ERROR.inc()
    elif 500 <= status_code < 600:
        HTTP_RESPONSES_SERVER_ERROR.inc()

    # Return the response back to the client
    return response


@app.route('/stock/<ticker>', methods=['GET'])
@REQUEST_LATENCY.time()
def get_stock_price(ticker):
    REQUEST_COUNT.inc()
    TICKER_REQUEST_COUNT.labels(ticker=ticker).inc()
    try:
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period='1mo')  # Fetch historical data for the last month
        if hist_data.empty:
            ERROR_COUNT.inc()
            return jsonify({"error": "Ticker not found"}), 404
        
        # Extracting closing prices, dates, and volume for the historical data
        hist_prices = hist_data['Close'].tolist()
        hist_dates = hist_data.index.strftime('%Y-%m-%d').tolist()
        hist_volume = hist_data['Volume'].tolist()
        # Fetch stock information
        info = stock.info
        # Get the most recent close price
        closing_price = hist_prices[-1] if hist_prices else None
        SUCCESS_COUNT.inc()
        return jsonify({
            "ticker": ticker,
            "current_price": closing_price,
            "history": {
                "dates": hist_dates,
                "prices": hist_prices
            },
            "volume": hist_volume,  # Trading volume
            "pe_ratio": info.get('trailingPE', 'N/A'),  # Price-to-earnings ratio
            "market_cap": info.get('marketCap', 'N/A'),  # Market capitalization
            "dividends": list(stock.dividends[-5:])  # Last 5 dividend payments
        })
    except Exception as e:
        ERROR_COUNT.inc()
        return jsonify({"error": str(e)}), 500


@app.route('/top-stocks', methods=['GET'])
def get_top_stocks():
    REQUEST_COUNT.inc()
    update_system_metrics()  # Update system metrics at the start of the request
    tickers = "AAPL MSFT GOOGL AMZN META"  # Example tickers
    try:
        data = yf.download(tickers, period='1d')['Close']
        # Convert index to string if it's a Timestamp
        if isinstance(data.index, pd.DatetimeIndex):
            data.index = data.index.strftime('%Y-%m-%d')
        results = data.to_dict()
        SUCCESS_COUNT.inc()
        update_system_metrics()  # Update metrics after processing
        return jsonify(results)
    except Exception as e:
        ERROR_COUNT.inc()
        return jsonify({"error": str(e), "failed_tickers": []}), 500
    
@app.route('/top-stocks/historical', methods=['GET'])
def get_historical_top_stocks():
    REQUEST_COUNT.inc()
    update_system_metrics()  # Update system metrics at the start of the request
    tickers = "AAPL MSFT GOOGL AMZN META"  # Example tickers
    try:
        data = yf.download(tickers, period='6mo', group_by='ticker')
        formatted_data = {ticker: data[ticker]['Close'].dropna().tolist() for ticker in tickers.split()}
        dates = [date.strftime('%Y-%m-%d') for date in data.index]
        SUCCESS_COUNT.inc()
        update_system_metrics()  # Update metrics after processing
        return jsonify({'data': formatted_data, 'dates': dates})
    except Exception as e:
        ERROR_COUNT.inc()
        return jsonify({"error": str(e), "failed_tickers": []}), 500
    
@app.route('/revenue-trends/<ticker>', methods=['GET'])
def get_revenue_trends(ticker):
    try:
        data, _ = fd.get_income_statement_annual(ticker)
        if 'annualReports' in data:
            revenue_data = [item['totalRevenue'] for item in data['annualReports']]
            dates = [item['fiscalDateEnding'] for item in data['annualReports']]
            return jsonify({"dates": dates, "revenue": revenue_data})
        else:
            return jsonify({"error": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/market-news', methods=['GET'])
def get_market_news():
    # Retrieve query parameters
    tickers = request.args.get('tickers', '').split(',') if request.args.get('tickers') else ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    time_from = request.args.get('time_from')
    time_to = request.args.get('time_to')
    sort = request.args.get('sort', 'LATEST')
    limit = int(request.args.get('limit', '50'))

    # Build query based on parameters
    query = News.query
    
    if tickers[0]:  # Check if tickers list is not empty
        query = query.filter(News.tickers.in_(tickers))
    if time_from:
        query = query.filter(News.posted_on >= datetime.strptime(time_from, '%Y-%m-%d'))
    if time_to:
        query = query.filter(News.posted_on <= datetime.strptime(time_to, '%Y-%m-%d'))
    
    # Sorting by date
    if sort == 'LATEST':
        query = query.order_by(News.posted_on.desc())
    else:
        query = query.order_by(News.posted_on)
    
    # Limiting results
    news_list = query.limit(limit).all()

    # Prepare response
    results = [{
        "title": news.title,
        "content": news.content,  # Changed from 'summary' to 'content' to match the database schema
        "posted_on": news.posted_on.strftime('%Y-%m-%d %H:%M:%S'),
        "tickers": news.tickers
    } for news in news_list]

    return jsonify(results)
    
@app.route('/earnings-insights', methods=['GET'])
def get_earnings_insights(ticker):
    REQUEST_COUNT.inc()
    try:
        data, _ = fd.get_company_overview(ticker)
        earnings_data = {
            "EPS": data.get("EPS"),
            "ProfitMargin": data.get("ProfitMargin"),
            "OperatingMarginTTM": data.get("OperatingMarginTTM"),
        }
        SUCCESS_COUNT.inc()
        return jsonify(earnings_data)
    except Exception as e:
        ERROR_COUNT.inc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return jsonify({"message": "Login successful", "user": user.username}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401
    
@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    portfolio_items = Portfolio.query.all()
    results = []
    for item in portfolio_items:
        stock = yf.Ticker(item.ticker)
        current_data = stock.history(period='1d')
        current_price = current_data['Close'].iloc[-1] if not current_data.empty else None
        if current_price:
            purchase_value = item.purchase_price * item.shares
            current_value = current_price * item.shares
            profit = current_value - purchase_value
            profit_percent = (profit / purchase_value) * 100
            results.append({
                "ticker": item.ticker,
                "shares": item.shares,
                "purchase_price": item.purchase_price,
                "current_price": current_price,
                "profit": profit,
                "profit_percent": profit_percent
            })
    return jsonify(results)


@app.route('/balance/<string:username>', methods=['GET'])
def get_balance(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"balance": user.balance}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/ticker-suggestions/<query>', methods=['GET'])
def get_ticker_suggestions(query):
    # Example static list of tickers, ideally, this could be dynamic or from the database
    all_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'FB', 'NFLX', 'INTC', 'CSCO', 'ORCL', 'IBM', 'NVDA', 'PYPL', 'ADBE', 'BABA']
    suggestions = [ticker for ticker in all_tickers if ticker.lower().startswith(query.lower())]
    return jsonify(suggestions)

@app.route('/stock-info/<ticker>', methods=['GET'])
def get_stock_info(ticker):
    # Directly querying for the admin user from the database
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        return jsonify({"error": "Admin user not found"}), 404

    stock = yf.Ticker(ticker)
    current_data = stock.history(period='1d')
    current_price = current_data['Close'].iloc[-1] if not current_data.empty else None

    if current_price is None:
        return jsonify({"error": "Could not fetch current price for the ticker."}), 404

    # Using the admin user's ID to filter the portfolio
    portfolio_entry = Portfolio.query.filter_by(ticker=ticker, user_id=admin_user.id).first()
    shares_owned = portfolio_entry.shares if portfolio_entry else 0

    return jsonify({
        "currentPrice": float(current_price),
        "sharesOwned": shares_owned
    })

@app.route('/buy', methods=['POST'])
def buy_stock():
    data = request.get_json()
    ticker = data.get('ticker')
    shares_to_buy = int(data.get('shares'))

    # Directly querying for the admin user from the database
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        return jsonify({"error": "Admin user not found"}), 404

    stock = yf.Ticker(ticker)
    current_data = stock.history(period='1d')
    current_price = current_data['Close'].iloc[-1] if not current_data.empty else None
    if not current_price:
        return jsonify({"error": "Failed to get current stock price"}), 404

    total_cost = shares_to_buy * current_price
    if admin_user.balance < total_cost:
        return jsonify({"error": "Insufficient balance"}), 400

    admin_user.balance -= total_cost
    portfolio_entry = Portfolio.query.filter_by(ticker=ticker, user_id=admin_user.id).first()
    if portfolio_entry:
        portfolio_entry.shares += shares_to_buy
    else:
        db.session.add(Portfolio(ticker=ticker, purchase_price=current_price, shares=shares_to_buy, user_id=admin_user.id))

    try:
        db.session.commit()
        return jsonify({"message": "Purchase successful", "new_balance": admin_user.balance}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/sell', methods=['POST'])
def sell_stock():
    data = request.get_json()
    ticker = data.get('ticker')
    shares_to_sell = int(data.get('shares'))

    # Directly querying for the admin user from the database
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        return jsonify({"error": "Admin user not found"}), 404

    stock = yf.Ticker(ticker)
    current_data = stock.history(period='1d')
    current_price = current_data['Close'].iloc[-1] if not current_data.empty else None
    if not current_price:
        return jsonify({"error": "Failed to get current stock price"}), 404

    portfolio_entry = Portfolio.query.filter_by(ticker=ticker, user_id=admin_user.id).first()
    if not portfolio_entry or portfolio_entry.shares < shares_to_sell:
        return jsonify({"error": "Not enough shares in portfolio"}), 400

    total_revenue = shares_to_sell * current_price
    admin_user.balance += total_revenue

    if portfolio_entry.shares > shares_to_sell:
        portfolio_entry.shares -= shares_to_sell
    else:
        db.session.delete(portfolio_entry)

    try:
        db.session.commit()
        return jsonify({"message": "Sale successful", "new_balance": admin_user.balance}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
