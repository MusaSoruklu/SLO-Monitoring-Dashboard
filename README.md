# SLO-Monitoring-Dashboard

The goal of this project is to combine knowledge of Site Reliability Engineering (SRE) with practical implementation by creating a comprehensive monitoring and alerting system for a web application.

The web application is a simple trading system that displays real-time stock data. A Python script is used to simulate random web server traffic. The system is designed to track key Service-Level Objectives (SLOs), such as response times and availability, ensuring that the web application operates within defined performance thresholds.


## Table of Contents

#### 🟣 &nbsp; [Installation and usage instructions](#1-installation-and-usage-instructions)
#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ◎ &nbsp; [Usage ]()
#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ◎ &nbsp; [Tools and dependencies]()


#### 🟣 &nbsp; [Project architecture](#2-project-architecture)
#### 🟣 &nbsp; [File structure of the project](#3-file-structure-of-the-project)
#### 🟣 &nbsp; [License information](#4-license-information)


## 1. Installation and usage instructions

### Tools and dependencies:

- **Jenkins :** Jenkins is an open-source automation server used for continuous integration and continuous delivery (CI/CD). It helps automate the building, testing, and deployment of applications. Documentation is available [here](https://www.jenkins.io/doc/)

- **Docker :** Docker is a platform that automates the deployment, scaling, and management of applications using containerisation. Containers bundle an application and its dependencies into a lightweight unit that can run consistently across various environments. Documentation is available [here](https://docs.docker.com/)

- **Prometheus :** Prometheus is an open-source monitoring and alerting toolkit designed for reliability and scalability. It is used to collect and store real-time metrics from the web application and system resources. Documentation is available [here](https://prometheus.io/docs/)

- **Grafana :** Grafana is an open-source analytics and monitoring platform that enables the creation of dynamic dashboards and visualisations. Documentation is available [here](https://grafana.com/docs/)


<div align="right">

[Back to top](#slo-monitoring-dashboard)
</div> 

## 2. Project architecture 



<div align="right">

[Back to top](#slo-monitoring-dashboard)
</div> 

## 3. File structure of the project

1. **web_traffic_simulator.py :** Script to simulate web server traffic and log response times to a SQLite database.

    - setup_database (function): Sets up the SQLite database to store response times, timestamps, and HTTP status codes.
    - random_delay (wrapper function): Adds a random delay between each HTTP request to simulate more realistic traffic patterns.
    - make_request (function): Sends an HTTP GET request to the web application. Logs the response time and status code to the SQLite database.
    - simulate_traffic (function): Simulates traffic by repeatedly calling make_request for the number of requests defined in NUM_REQUESTS.

1. **JenkinsFIle :** Defines a Jenkins pipeline for building and pushing Docker images for frontend and backend applications.

    - Checkout SCM (stage): Retrieves the source code from the specified Git repository using the 'main' branch and provided credentials.
    - Build Backend (stage): Builds the Docker image for the backend application and tags it with the current build number.
    - Build Frontend (stage): Builds the Docker image for the frontend application and tags it with the current build number.
    - Push Backend (stage): Pushes the backend Docker image to the Docker registry.
    - Push Frontend (stage): Pushes the frontend Docker image to the Docker registry.
    - Post Actions (post): Cleans up the workspace after the build process is complete.

1. 

<div align="right">

[Back to top](#slo-monitoring-dashboard)
</div> 

## 4. License information
GNU General Public License (GPL) v3.0

<div align="right">

[Back to top](#slo-monitoring-dashboard)
</div> 