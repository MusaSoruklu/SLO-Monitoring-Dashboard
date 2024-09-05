
# SLO Monitoring Dashboard

## Overview

This project is a complete stack monitoring dashboard application that allows users to monitor stock market performance, news, and personal portfolios. The application is divided into two parts:

- **Backend**: A Flask-based API that provides stock data, news, and portfolio information using `yfinance`, `Alpha Vantage`, and Prometheus for monitoring.
- **Frontend**: An Angular-based dashboard that offers an interface to view the data provided by the backend.

## Features

### Backend
- Stock information retrieval via `yfinance`.
- Stock fundamental data via Alpha Vantage API.
- News and portfolio management using `Flask-SQLAlchemy`.
- Prometheus metrics integration for monitoring system performance.
- User authentication and portfolio tracking.
- Flask CORS support for cross-origin requests.
- Exposes metrics for Prometheus, including custom metrics such as memory usage, CPU usage, and HTTP status codes.

### Frontend
- Built with Angular for a responsive user interface.
- Displays real-time stock data and news.
- Allows users to view and manage their stock portfolios.

## Application Architecture

The application is composed of two major components:
1. **Backend (Flask API)**: Provides APIs for stock data, portfolio management, user login, and news.
2. **Frontend (Angular)**: Displays stock data, market trends, and portfolio information to the user.

### Folder Structure
```
SLO-MONITORING-DASHBOARD/
├── backend/                    # Flask Backend
│   ├── app.py                  # Main Flask app
│   ├── Dockerfile              # Dockerfile for Backend
│   ├── requirements.txt        # Python dependencies
│   └── prometheus.yml          # Prometheus configuration
├── frontend/                   # Angular Frontend
│   ├── src/                    # Angular source code
│   ├── Dockerfile              # Dockerfile for Frontend
│   ├── nginx.conf              # Custom Nginx configuration
│   └── angular.json            # Angular project configuration
├── docker-compose.yml          # Docker Compose configuration for both backend and frontend
├── slo-monitoring-dashboard.yaml  # Kubernetes deployment YAML file
└── README.md                   # Project documentation
```

## Backend Setup

### Prerequisites
- Python 3.9+
- Docker

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/slo-monitoring-dashboard.git
   cd slo-monitoring-dashboard/backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the application:
   ```bash
   flask run
   ```

4. Access the Prometheus metrics at `http://localhost:8000/metrics`.

### API Endpoints

- `/stock/<ticker>`: Fetch stock data for the given ticker.
- `/top-stocks`: Fetch top stock data.
- `/market-news`: Get the latest market news.
- `/portfolio`: Get the current portfolio of the logged-in user.
- `/buy`: Buy stock for the user.
- `/sell`: Sell stock for the user.

### Prometheus Metrics

The backend integrates with Prometheus for monitoring. Metrics are exposed at `/metrics` and include:

- Request count and latency.
- Memory and CPU usage.
- HTTP status code counters.

## Frontend Setup

### Prerequisites
- Node.js 18.x+
- Angular CLI

### Installation

1. Navigate to the `frontend` directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   ng serve
   ```

4. Open `http://localhost:4200` to view the application.

## Running with Docker

You can easily run both the frontend and backend with Docker using either Docker Compose or Kubernetes.

### Docker Compose

1. Ensure Docker is installed and running on your system.
2. Run the following command to build and start the containers:
   ```bash
   docker-compose up --build
   ```

3. Access the frontend at `http://localhost:80` and the backend at `http://localhost:8001`.

### Kubernetes

1. Deploy the application using the provided Kubernetes YAML file:
   ```bash
   kubectl apply -f slo-monitoring-dashboard.yaml
   ```

2. Kubernetes will manage the frontend and backend as services. Adjust the `slo-monitoring-dashboard.yaml` file to configure scaling, ingress, and other settings as needed.



## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.



