pipeline {
    agent any

    environment {

    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/your-repo/SLO-Monitoring-Dashboard.git'
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

        stage('Deploy to Kubernetes') {
            steps {
                withKubeConfig(credentialsId: KUBECONFIG_CREDENTIALS_ID) {
                    sh 'kubectl apply -f kubernetes/deployment.yaml'
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
