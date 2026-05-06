pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "iamruparc/music-recommendation"
        DOCKER_TAG = "v1.${BUILD_NUMBER}"
        SONAR_PROJECT_KEY = "music-recommendation"
        CONTAINER_NAME = "music-recommendation"
        AWS_REGION = "ap-south-1"
        EKS_CLUSTER = "music-cluster"
        K8S_NAMESPACE = "music-app"
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'devops',
                    credentialsId: 'github-creds',
                    url: 'https://github.com/rup-arc/music_recommendation_sys.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarqube-server') {
                    sh '''
                        sonar-scanner \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=${SONAR_HOST_URL} \
                        -Dsonar.login=${SONAR_AUTH_TOKEN}
                    '''
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    DOCKER_BUILDKIT=0 docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                    mkdir -p reports
                    trivy image \
                    --format table \
                    --output reports/trivy-report.txt \
                    --severity HIGH,CRITICAL \
                    --exit-code 0 \
                    ${DOCKER_IMAGE}:${DOCKER_TAG}
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/trivy-report.txt'
                }
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    retry(3) {
                        sh '''
                            echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                            docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                            docker push ${DOCKER_IMAGE}:latest
                        '''
                    }
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                withCredentials([
                    file(credentialsId: 'env-file', variable: 'ENV_FILE')
                ]) {
                    sh '''
                        # Connect Jenkins to EKS
                        aws eks update-kubeconfig \
                            --region ${AWS_REGION} \
                            --name ${EKS_CLUSTER}

                        # Create namespace if not exists
                        kubectl create namespace ${K8S_NAMESPACE} \
                            --dry-run=client -o yaml | kubectl apply -f -

                        # Create secret from env file
                        kubectl create secret generic music-app-secret \
                            --from-env-file=$ENV_FILE \
                            --namespace=${K8S_NAMESPACE} \
                            --dry-run=client -o yaml | kubectl apply -f -

                        # Update image tag in deployment
                        sed -i "s|IMAGE_TAG|${DOCKER_TAG}|g" k8s/deployment.yaml

                        # Apply K8s manifests
                        kubectl apply -f k8s/ --namespace=${K8S_NAMESPACE}

                        # Wait for rollout
                        kubectl rollout status deployment/music-recommendation \
                            --namespace=${K8S_NAMESPACE} \
                            --timeout=300s
                    '''
                }
            }
        }

    }

    post {
        always {
            sh 'docker logout'
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        success {
            echo "Pipeline succeeded! App deployed to EKS!"
        }
        failure {
            echo "Pipeline failed! Check the logs above."
        }
        cleanup {
            sh '''
                docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                docker image prune -f || true
            '''
        }
    }

}
