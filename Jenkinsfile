pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'my-docker-credentials'  // Use the ID you set in Jenkins
        GITHUB_CREDENTIALS_ID = 'github-token'  // Use the ID you created in the previous step
        DOCKER_REGISTRY = 'mnikkilla'  // Your Docker Hub username
        FRONTEND_IMAGE = "${DOCKER_REGISTRY}/frontend"  // Replace with your frontend repo name
        BACKEND_IMAGE = "${DOCKER_REGISTRY}/backend"  // Replace with your backend repo name
    }

    stages {
        stage('Checkout SCM') {
            steps {
                git branch: 'main',
                    url: 'git@github.com:MusaSoruklu/SLO-Monitoring-Dashboard.git',
                    credentialsId: 'ssh-id'  // Updated to use PAT for authentication
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
        
        stage('Deploy on EC2') {
            steps {
                sh '''
                    # Navigate to the directory where the docker-compose.yml file is located
                    cd "/var/lib/jenkins/workspace/Job 1"
            
                    # Stop the running containers
                    docker-compose down
            
                    # Update docker-compose.yml with the latest build number for frontend and backend
                    sed -i 's|mnikkilla/frontend:16|mnikkilla/frontend:'"${BUILD_NUMBER}"'|' docker-compose.yml
                    sed -i 's|mnikkilla/backend:16|mnikkilla/backend:'"${BUILD_NUMBER}"'|' docker-compose.yml
            
                    # Pull the latest images from Docker Hub
                    docker-compose pull
            
                    # Start the containers with the latest images in detached mode
                    docker-compose up -d
            
                    # Optionally, check the status of the containers
                    docker-compose ps
                '''
            }
        }
    }

    // post {
    //     always {
    //         cleanWs()
    //     }
    // }
}
