pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "iamruparc/music-recommendation"
        DOCKER_TAG = "v1.${BUILD_NUMBER}"
        SONAR_PROJECT_KEY = "music-recommendation"
        CONTAINER_NAME = "music-recommendation"
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

        stage('OWASP Dependency Check') {
            steps {
                dependencyCheck additionalArguments: '''
                    --scan .
                    --format HTML
                    --format XML
                    --out reports/
                    --prettyPrint
                ''', odcInstallation: 'owasp-dependency-check'
                dependencyCheckPublisher pattern: 'reports/dependency-check-report.xml'
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
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
                    --exit-code 1 \
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
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker pull ${DOCKER_IMAGE}:latest
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 5000:5000 \
                        --restart unless-stopped \
                        ${DOCKER_IMAGE}:latest
                '''
            }
        }

    }

    post {
        always {
            sh 'docker logout'
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        success {
            echo "Pipeline succeeded! App running at http://localhost:5000"
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