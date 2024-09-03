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

@app.route('/stock/<ticker>', methods=['GET'])
@REQUEST_LATENCY.time()
def get_stock_price(ticker):
    REQUEST_COUNT.inc()
    TICKER_REQUEST_COUNT.labels(ticker=ticker).inc()
    try:
        stock = yf.Ticker(ticker)
        # Fetch historical data for the last month
        hist_data = stock.history(period='1mo')
        
        if hist_data.empty:
            ERROR_COUNT.inc()
            return jsonify({"error": "Ticker not found"}), 404
        
        # Extracting closing prices and dates for the historical data
        hist_prices = hist_data['Close'].tolist()
        hist_dates = hist_data.index.strftime('%Y-%m-%d').tolist()

        # Get the most recent close price
        closing_price = hist_prices[-1] if hist_prices else None

        SUCCESS_COUNT.inc()
        return jsonify({
            "ticker": ticker,
            "current_price": closing_price,
            "history": {
                "dates": hist_dates,
                "prices": hist_prices
            }
        })
    except Exception as e:
        ERROR_COUNT.inc()
        return jsonify({"error": str(e)}), 500


@app.route('/top-stocks', methods=['GET'])
def get_top_stocks():
    REQUEST_COUNT.inc()
    tickers = "AAPL MSFT GOOGL AMZN META"  # Example tickers
    try:
        data = yf.download(tickers, period='1d')['Close']
        # Convert index to string if it's a Timestamp
        if isinstance(data.index, pd.DatetimeIndex):
            data.index = data.index.strftime('%Y-%m-%d')
        results = data.to_dict()
        SUCCESS_COUNT.inc()
        return jsonify(results)
    except Exception as e:
        ERROR_COUNT.inc()
        return jsonify({"error": str(e), "failed_tickers": []}), 500
    
@app.route('/top-stocks/historical', methods=['GET'])
def get_historical_top_stocks():
    REQUEST_COUNT.inc()
    tickers = "AAPL MSFT GOOGL AMZN META"  # Example tickers
    try:
        data = yf.download(tickers, period='6mo', group_by='ticker')
        formatted_data = {ticker: data[ticker]['Close'].dropna().tolist() for ticker in tickers.split()}
        dates = [date.strftime('%Y-%m-%d') for date in data.index]
        SUCCESS_COUNT.inc()
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


if __name__ == '__main__':
    app.run(debug=True)
