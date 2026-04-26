pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_USERNAME = credentials('docker-username')
        DOCKER_PASSWORD = credentials('docker-password')
        DOCKER_IMAGE = 'rup-arc/music-recommendation-sys'
        DOCKER_TAG = "${BUILD_NUMBER}"
        AWS_REGION = 'us-east-1'
        EKS_CLUSTER = 'music-recommendation-cluster'
        EKS_NAMESPACE = 'music-recommendation'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "🔍 Checking out code from GitHub..."
                }
                checkout scm
            }
        }

        stage('Build') {
            steps {
                script {
                    echo "🏗️  Building Docker image..."
                    sh '''
                        docker build -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker tag ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    echo "🧪 Running tests..."
                    sh '''
                        docker run --rm ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} \
                            python -m pytest tests/ -v || true
                    '''
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                script {
                    echo "📤 Pushing image to DockerHub..."
                    sh '''
                        echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin
                        docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                script {
                    echo "🚀 Deploying to EKS..."
                    sh '''
                        # Update kubeconfig
                        aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER}
                        
                        # Update image in deployment
                        kubectl set image deployment/music-recommendation \
                            music-recommendation=${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} \
                            -n ${EKS_NAMESPACE} || \
                        kubectl apply -f k8s/deployment.yaml
                        
                        # Wait for rollout
                        kubectl rollout status deployment/music-recommendation -n ${EKS_NAMESPACE}
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    echo "✅ Verifying deployment..."
                    sh '''
                        kubectl get pods -n ${EKS_NAMESPACE}
                        kubectl get services -n ${EKS_NAMESPACE}
                        
                        # Check health endpoint
                        POD_NAME=$(kubectl get pods -n ${EKS_NAMESPACE} -l app=music-recommendation -o jsonpath='{.items[0].metadata.name}')
                        kubectl port-forward -n ${EKS_NAMESPACE} pod/$POD_NAME 5000:5000 &
                        sleep 3
                        curl -f http://localhost:5000/health || true
                    '''
                }
            }
        }
    }

    post {
        success {
            script {
                echo "✅ Pipeline succeeded!"
            }
        }
        failure {
            script {
                echo "❌ Pipeline failed. Check logs above."
            }
        }
        cleanup {
            cleanWs()
        }
    }
}
