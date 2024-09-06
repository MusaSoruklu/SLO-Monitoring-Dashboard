import requests
import time
import random
from datetime import datetime

# CONFIGURATION 
WEB_APP_URL = "http://localhost:5000"              # TODO: Replace with web application's URL
NUM_REQUESTS = 300  # Number of requests to simulate
MIN_DELAY = 1  # Minimum delay between requests in seconds
MAX_DELAY = 5  # Maximum delay between requests in seconds
URL_ENDPOINTS = ["/metrics", "/stock/AAPL", "/top-stocks", "/revenue-trends/AAPL"]  # List of endpoints


# TO SIMULATE TRAFFIC : simulate_traffic function calls make_request function for a certain number of requests. 
# Make_request function has a wrapper to add random delays between requests 

def random_delay(func):
    """Decorator function / wrapper to add random delays between requests."""
    def wrapper(*args, **kwargs):
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        print(f"Waiting for {delay:.2f} seconds before next request...")
        time.sleep(delay)
        return func(*args, **kwargs)
    return wrapper

@random_delay
def make_request():
    """Sends an HTTP GET request to a random endpoint of the web application and logs the response time."""
    endpoint = random.choice(URL_ENDPOINTS)
    url = f"{WEB_APP_URL}{endpoint}"
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()
    response_time = end_time - start_time


    # Print response results
    print(f"Endpoint = {endpoint}, Response Time = {response_time:.4f} seconds, Status Code = {response.status_code}")

# Simulate traffic function calls make_request function 
def simulate_traffic():
    """Simulates traffic by making repeated HTTP GET requests to random endpoints of the web application."""
    for i in range(NUM_REQUESTS):
        print(f"Request {i+1}/{NUM_REQUESTS}:")
        make_request()

if __name__ == "__main__":
    simulate_traffic()
