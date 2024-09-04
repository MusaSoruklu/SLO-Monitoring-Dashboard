import requests
import time
import sqlite3
import random
from datetime import datetime

# CONFIGURATION 
WEB_APP_URL = "http://localhost:5000"              # TODO: Replace with web application's URL
NUM_REQUESTS = 300  # Number of requests to simulate
MIN_DELAY = 1  # Minimum delay between requests in seconds
MAX_DELAY = 5  # Maximum delay between requests in seconds
DATABASE = "traffic_data.db"  # SQLite database file  # TODO: merge with DB in backend code  

URL_ENDPOINT = None                             # TODO: Add endpoints

# DATABASE SETUP                                TODO: (similar to prometheus?)
def setup_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS response_times (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        response_time FLOAT,
                        status_code INTEGER
                      )''')
    conn.commit()
    conn.close()


# TO SIMULATE TRAFFIC : simulate_traffic function calls make_request function for a certain number of requests. 
# Make_request function has a wrapper to add random delays between requests 

def random_delay(func):
    """Decorator function / wrapper to add a random delays between requests."""
    def wrapper(*args, **kwargs):
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        print(f"Waiting for {delay:.2f} seconds before next request...")
        time.sleep(delay)
        return func(*args, **kwargs)
    return wrapper

@random_delay
def make_request():
    """Sends an HTTP GET request to the web application and logs the response time."""
    start_time = time.time()
    response = requests.get(WEB_APP_URL)
    end_time = time.time()
    response_time = end_time - start_time

    # Log the result to the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO response_times (timestamp, response_time, status_code) 
                      VALUES (?, ?, ?)''',
                   (datetime.now(), response_time, response.status_code))
    conn.commit()
    conn.close()

    print(f"Response Time = {response_time:.4f} seconds, Status Code = {response.status_code}")

# Simulate traffic function calls make_request function 
def simulate_traffic():
    """Simulates traffic by making repeated HTTP GET requests to the web application."""
    for i in range(NUM_REQUESTS):
        print(f"Request {i+1}/{NUM_REQUESTS}:")
        make_request()

if __name__ == "__main__":
    setup_database()
    simulate_traffic()
