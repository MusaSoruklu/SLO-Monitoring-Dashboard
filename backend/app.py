from flask import Flask, jsonify
import yfinance as yf
import pandas as pd
from prometheus_client import start_http_server, Summary, Counter, Gauge, generate_latest
from flask_cors import CORS
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all domains on all routes

# Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'Total number of requests')
REQUEST_LATENCY = Summary('request_latency_seconds', 'Time spent processing request')
ERROR_COUNT = Counter('error_count', 'Total number of errors')
SUCCESS_COUNT = Counter('success_count', 'Total number of successful requests')
TICKER_REQUEST_COUNT = Counter('ticker_request_count', 'Number of requests per ticker', ['ticker'])

api_key = 'Q7C09DFLJD3WH0GC'
ts = TimeSeries(key=api_key)
fd = FundamentalData(key=api_key)

# Start a Prometheus metrics server on port 8000
start_http_server(8000)

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.route('/stock/<ticker>', methods=['GET'])
@REQUEST_LATENCY.time()
def get_stock_price(ticker):
    REQUEST_COUNT.inc()
    try:
        TICKER_REQUEST_COUNT.labels(ticker=ticker).inc()
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d')
        if data.empty:
            ERROR_COUNT.inc()
            return jsonify({"error": "Ticker not found"}), 404
        closing_price = data['Close'][0]
        SUCCESS_COUNT.inc()
        return jsonify({
            "ticker": ticker,
            "closing_price": closing_price
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
    tickers = request.args.get('tickers', 'AAPL,MSFT,GOOGL,AMZN,META')
    topics = request.args.get('topics', '')
    time_from = request.args.get('time_from', '')
    time_to = request.args.get('time_to', '')
    sort = request.args.get('sort', 'LATEST')
    limit = request.args.get('limit', '50')

    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": tickers,
        "topics": topics,
        "time_from": time_from,
        "time_to": time_to,
        "sort": sort,
        "limit": limit,
        "apikey": api_key
    }

    try:
        response = requests.get("https://www.alphavantage.co/query", params=params)
        if response.status_code == 200:
            # Manually setting CORS headers
            return Response(response.content, mimetype='application/json', headers={"Access-Control-Allow-Origin": "*"})
        else:
            return jsonify({"error": "Failed to fetch market news", "status_code": response.status_code}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/earnings-insights/<ticker>', methods=['GET'])
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


if __name__ == '__main__':
    app.run(debug=True)
