# GVisit - Modern Digital Journal & Presentation Platform

[![CI/CD Pipeline](https://github.com/Dr-Payne25/GVisit/actions/workflows/ci.yml/badge.svg)](https://github.com/Dr-Payne25/GVisit/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-ready Flask application featuring a Baronfig-inspired digital journal, secure presentation hosting, and enterprise-grade infrastructure integration with AWS services.

## 🌟 Features

### Core Functionality
- **Digital Journal**: Baronfig-inspired journal with mood tracking, gratitude sections, and guided prompts
- **Secure Presentations**: Password-protected PowerPoint file hosting with secure download mechanisms
- **Modern UI**: Dark theme with Bootstrap 5, responsive design inspired by Apple's aesthetic

### Infrastructure & DevOps
- **Docker Support**: Fully containerized with Docker and docker-compose
- **AWS Integration**: 
  - S3 automatic backups with lifecycle policies
  - Optional DynamoDB storage backend
  - IAM security best practices
- **Infrastructure as Code**: Terraform configurations for AWS resources
- **Production Ready**: Gunicorn WSGI server, health checks, environment-based configuration

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Browser   │────▶│ Flask App    │────▶│ Local JSON  │
└─────────────┘     │ (Gunicorn)   │     └─────────────┘
                    └──────┬───────┘              │
                           │                      │ Backup
                    ┌──────▼───────┐              ▼
                    │   AWS S3     │     ┌─────────────┐
                    │   Backups    │     │ S3 Bucket   │
                    └──────────────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │  DynamoDB    │
                    │  (Optional)  │
                    └──────────────┘
```

## 🚀 Quick Start

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gvisit.git
cd gvisit
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Run the application:
```bash
python3 app.py
```

4. Access the application at `http://localhost:5002`

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Access the application at `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# AWS Configuration (Optional)
S3_BACKUP_BUCKET=gvisit-journal-backups
AWS_REGION=us-east-1

# DynamoDB Configuration (Optional)
USE_DYNAMODB=false
DYNAMODB_TABLE_NAME=gvisit-journal-entries

# Application Configuration
PASSWORD=GVISIT
PORT=8000
```

### AWS Setup

1. Configure AWS credentials:
```bash
aws configure
```

2. Deploy infrastructure with Terraform:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## 📝 Journal Entry Structure

Each journal entry captures:
- **Focus/Prompt**: Guided prompts for different reflection types
- **Content**: Main reflection text
- **Mood Tracking**: 5-level mood indicator
- **Energy Level**: High/Medium/Low energy tracking
- **Gratitude Section**: Up to 3 gratitude items
- **Action Item**: Next step or key takeaway

## 🔒 Security Features

- Session-based authentication for presentations
- Secure file storage outside public directories
- AWS IAM least-privilege policies
- Server-side encryption for S3 backups
- Environment-based secret management

## 📊 Monitoring & Health

- Health check endpoint: `/health`
- Structured logging with Python logging module
- Docker health checks for container orchestration
- S3 backup status monitoring

## 🚢 Deployment Options

### AWS EC2
```bash
# Install Docker on EC2
sudo yum update -y
sudo yum install docker -y
sudo service docker start

# Deploy application
docker-compose up -d
```

### AWS ECS
- Use the provided Dockerfile
- Configure task definitions with environment variables
- Set up ALB for load balancing

### Heroku
```bash
# Create Heroku app
heroku create your-app-name

# Deploy
git push heroku main
```

## 🧪 Testing

Run the application and test:
1. Create journal entries with different prompts
2. Test password protection (default: "GVISIT")
3. Verify S3 backups if configured
4. Check health endpoint: `curl http://localhost:5002/health`

## 📚 Tech Stack

- **Backend**: Python 3.9, Flask 2.3.3
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Database**: JSON file storage, optional DynamoDB
- **Infrastructure**: Docker, AWS (S3, DynamoDB, IAM)
- **IaC**: Terraform
- **Web Server**: Gunicorn

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Future Enhancements

- [ ] User authentication system
- [ ] Export journal entries to PDF
- [ ] Analytics dashboard for mood/energy trends
- [ ] Mobile app with offline sync
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Vault integration for secret management

## 👨‍💻 About This Project

This project demonstrates:
- **Full-stack development** with Python/Flask
- **Cloud architecture** with AWS services
- **DevOps practices** with Docker and Terraform
- **Security best practices** for web applications
- **Modern UI/UX** design principles

Perfect for showcasing SRE/Senior Python Engineer capabilities including infrastructure automation, cloud services integration, and production-ready application development. 