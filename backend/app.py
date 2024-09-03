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

    def __repr__(self):
        return f'<User {self.username}>'
    
@app.cli.command('init-db')
def init_db_command():
    """Initialize the database and seed it with default user and news data if they don't exist."""
    db.create_all()  # This will not affect existing tables and data
    print('Checked and ensured all tables are created.')

    # Check if default user exists
    if User.query.filter_by(username='admin').first() is None:
        default_user = User(username='admin', password='admin')  # Note: Plain text password is not secure
        db.session.add(default_user)
        db.session.commit()
        print('Added default admin user.')

    # Check if there are any news entries
    if News.query.count() == 0:
        # Sample news data
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

@app.route('/metrics')
def metrics():
    return generate_latest()

def update_system_metrics():
    process = os.getpid()

    # Attempt to get memory usage
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
    except Exception as e:
        print(f"Error fetching memory info: {e}")

    # Get CPU usage, simpler method
    try:
        cpu_usage = os.getloadavg()[0] * 100  # Simple example using load average on Unix
        CPU_USAGE.set(cpu_usage)
    except Exception as e:
        print(f"Error fetching CPU usage: {e}")

@app.route('/stock/<ticker>', methods=['GET'])
@REQUEST_LATENCY.time()
def get_stock_price(ticker):
    REQUEST_COUNT.inc()
    TICKER_REQUEST_COUNT.labels(ticker=ticker).inc()
    update_system_metrics()  # Update system metrics at the start of the request

    try:
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period='1mo')  # Fetch historical data for the last month

        if (hist_data.empty):
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
        update_system_metrics()  # Update metrics after processing
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
        return jsonify({"error": str(e), "failed_tickers": []}),
