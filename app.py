from flask import Flask, jsonify
import yfinance as yf
import pandas as pd
from prometheus_client import start_http_server, Summary, Counter, Gauge, generate_latest
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'Total number of requests')
REQUEST_LATENCY = Summary('request_latency_seconds', 'Time spent processing request')
ERROR_COUNT = Counter('error_count', 'Total number of errors')
SUCCESS_COUNT = Counter('success_count', 'Total number of successful requests')
TICKER_REQUEST_COUNT = Counter('ticker_request_count', 'Number of requests per ticker', ['ticker'])

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

if __name__ == '__main__':
    app.run(debug=True)
