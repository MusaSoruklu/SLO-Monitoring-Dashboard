
# SLO Monitoring Dashboard

## Overview

![Dashboard Screenshot](./Documents/dash.png)
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
   
## CI/CD Architecture
The system is built using Docker, Jenkins, and Kubernetes for scalability and CI/CD.
1. **Docker**: Containerizes the application, managing the backend, frontend, and other services. The `docker-compose.yml` file orchestrates the containers.
2. **Jenkins**: Automates the CI/CD pipeline, building, testing, and deploying the application via Docker.
3. **Kubernetes**: Manages deployment, scaling, and monitoring of containers in production, using the `slo-monitoring-dashboard.yaml` configuration.

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

4. Access the Prometheus metrics at `http://localhost:5000/metrics`.

### API Endpoints

- `/stock/<ticker>`: Fetch stock data for the given ticker.
- `/top-stocks`: Fetch top stock data.
- `/market-news`: Get the latest market news.
- `/portfolio`: Get the current portfolio of the logged-in user.
- `/buy`: Buy stock for the user.
- `/sell`: Sell stock for the user.


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


## Monitoring and Metrics

This project leverages **Prometheus** for collecting application and system metrics, and **Grafana** for visualizing these metrics. The backend exposes various Prometheus metrics related to system performance and HTTP requests, which can be monitored and visualized in Grafana.

### Prometheus Metrics
The backend integrates with Prometheus for monitoring. Metrics are exposed at `/metrics` and include:

- **Request Count**: Total number of requests to the backend API.
- **Request Latency**: Time spent processing each request.
- **Error Count**: Total number of errors in API responses.
- **Custom Metrics**:
  - **Memory Usage (RSS and VMS)**: Tracks memory consumption.
  - **CPU Usage**: Tracks CPU usage.
  - **HTTP Status Codes**: Counters for informational (1xx), successful (2xx), redirection (3xx), client error (4xx), and server error (5xx) responses.

### Grafana Dashboard

A Grafana dashboard is used to visualize these metrics. You can access metrics such as request counts, error rates, memory consumption, and CPU usage from the Prometheus backend in real-time.

Here’s an example of how the Grafana dashboard might look:

![Grafana Dashboard](./Documents/Grafana-dash.png)
![Grafana Dashboard](./Documents/Grafana-dash1.png)

### Services Overview

This project comprises four Docker services:
1. **Backend Service (Flask API)**: Exposes API endpoints for stock data, portfolio management, and news.
2. **Frontend Service (Angular)**: Serves the user interface for the dashboard.
3. **Prometheus**: Scrapes metrics from the backend and other services.
4. **Grafana**: Visualizes the metrics from Prometheus.

These services are integrated using Docker Compose, and Prometheus automatically scrapes the metrics provided by the backend API at `/metrics`.
"""
## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.



