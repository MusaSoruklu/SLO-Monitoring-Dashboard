pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'my-docker-credentials'  // Use the ID you set in Jenkins
        DOCKER_REGISTRY = 'saeidnkh'  // Your Docker Hub username
        FRONTEND_IMAGE = "${DOCKER_REGISTRY}/frontend"  // Replace with your frontend repo name
        BACKEND_IMAGE = "${DOCKER_REGISTRY}/backend"  // Replace with your backend repo name
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/MusaSoruklu/SLO-Monitoring-Dashboard.git'
            }
        }

        stage('Build Backend') {
            steps {
                script {
                    docker.build("${BACKEND_IMAGE}:${env.BUILD_NUMBER}", './backend')
                }
            }
        }

        stage('Build Frontend') {
            steps {
                script {
                    docker.build("${FRONTEND_IMAGE}:${env.BUILD_NUMBER}", './frontend')
                }
            }
        }

        stage('Push Backend') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS_ID) {
                        docker.image("${BACKEND_IMAGE}:${env.BUILD_NUMBER}").push()
                    }
                }
            }
        }

        stage('Push Frontend') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS_ID) {
                        docker.image("${FRONTEND_IMAGE}:${env.BUILD_NUMBER}").push()
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
