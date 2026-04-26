# Music Recommendation System

A Flask-based music recommendation system with CI/CD pipeline, deployed on AWS EKS with CloudWatch monitoring.

## Architecture

- **Frontend**: Flask web application with HTML/CSS/JavaScript
- **Backend**: Python Flask API with pandas for data processing
- **Data Storage**: AWS S3 for dataset storage
- **Containerization**: Docker with multi-stage builds
- **CI/CD**: Jenkins with GitHub integration
- **Deployment**: AWS EKS (Kubernetes)
- **Monitoring**: CloudWatch logs, metrics, and alarms
- **Infrastructure**: Terraform for IaC

## Prerequisites

- AWS CLI configured
- Docker installed
- kubectl installed
- Terraform installed
- GitHub repository

## Quick Start

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python run.py
```

### 2. Docker Setup

```bash
# Build and run with Docker
docker-compose up -d
```

### 3. Jenkins Setup

```bash
# Start Jenkins
docker-compose -f docker-compose.yml up -d

# Access Jenkins at http://localhost:8080
# Initial password: admin/admin
```

### 4. Infrastructure Deployment

```bash
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="alert_email=your-email@example.com"

# Apply infrastructure
terraform apply -var="alert_email=your-email@example.com"
```

### 5. Kubernetes Deployment

```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name music-recommendation-cluster

# Deploy application
kubectl apply -f k8s/

# Check deployment
kubectl get pods -n music-recommendation
kubectl get services -n music-recommendation
```

## Configuration

### Environment Variables

- `FLASK_ENV`: Environment (development/production)
- `AWS_REGION`: AWS region (default: us-east-1)
- `S3_BUCKET`: S3 bucket name for data
- `S3_KEY`: S3 object key for dataset
- `LOG_GROUP`: CloudWatch log group name

### Jenkins Credentials

Set up these credentials in Jenkins:
- `docker-username`: Docker Hub username
- `docker-password`: Docker Hub password/token

## API Endpoints

- `GET /`: Main page
- `POST /recommend`: Get music recommendations
- `GET /search`: Search songs
- `GET /health`: Health check

## Monitoring

### CloudWatch Dashboard

Access the CloudWatch dashboard at:
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=music-recommendation-dashboard

### Logs

Application logs are available in CloudWatch Logs:
- Log Group: `/ecs/music-recommendation`

### Alarms

- High CPU utilization (>80%)
- High memory utilization (>80%)

## CI/CD Pipeline

The Jenkins pipeline includes:
1. Code checkout from GitHub
2. Docker image build
3. Unit testing
4. Push to Docker Hub
5. Deploy to EKS
6. Health verification

## File Structure

```
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── run.py                # Development runner
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Local Docker setup
├── Jenkinsfile           # CI/CD pipeline
├── terraform/            # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── s3.tf
│   └── backend.tf
├── k8s/                  # Kubernetes manifests
│   ├── deployment.yaml
│   ├── rbac.yaml
│   ├── configmap.yaml
│   └── ingress.yaml
├── static/               # Static assets
├── templates/            # HTML templates
├── data/                 # Dataset
└── .gitignore           # Git ignore rules
```

## Security

- Non-root container execution
- IAM roles for service accounts (IRSA)
- S3 bucket encryption
- Private subnets for EKS nodes
- Security groups and network policies

## Troubleshooting

### Common Issues

1. **Jenkins can't connect to Docker**:
   ```bash
   # Add jenkins user to docker group
   docker exec -it jenkins-music-app usermod -aG docker jenkins
   ```

2. **EKS cluster access**:
   ```bash
   # Update kubeconfig
   aws eks update-kubeconfig --region us-east-1 --name music-recommendation-cluster
   ```

3. **S3 access denied**:
   - Ensure IAM role has S3 read permissions
   - Check bucket name in environment variables

4. **CloudWatch logs not appearing**:
   - Verify IAM role has CloudWatch permissions
   - Check log group name configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test locally
4. Push to GitHub and create PR
5. Jenkins will run CI/CD pipeline

## License

MIT License