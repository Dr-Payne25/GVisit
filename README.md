# GVisit - Modern Digital Journal & Presentation Platform

[![CI/CD Pipeline](https://github.com/Dr-Payne25/GVisit/actions/workflows/ci.yml/badge.svg)](https://github.com/Dr-Payne25/GVisit/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-ready-orange.svg)](https://aws.amazon.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern web application featuring secure password-protected presentations and a personal digital journal with user authentication.

## 🚀 Features

### 📔 Digital Journal
- **Secure User Authentication**: Individual accounts with password hashing
- **Case-Insensitive Usernames**: Better user experience
- **Private Entries**: Each user has their own journal space
- **Structured Journaling**: Multiple focus types (Daily Reflection, Weekly Goals, etc.)
- **Mood & Energy Tracking**: Track your emotional and physical state
- **Gratitude Lists**: Record what you're thankful for
- **Action Items**: Set goals for tomorrow
- **Collapsible Entry View**: Clean interface showing titles by default

### 🎯 Presentation Platform

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

Run unit tests:
```bash
pytest tests/ -v --cov=.
```

## 🔄 CI/CD Pipeline

The project includes a comprehensive GitHub Actions CI/CD pipeline that runs on every push to main/develop branches:

### Pipeline Stages

1. **Code Quality**
   - Black formatter check
   - isort import sorting
   - Flake8 linting
   - Bandit security analysis

2. **Testing**
   - Multi-version Python testing (3.8, 3.9, 3.10)
   - Unit tests with pytest
   - Code coverage reporting with Codecov

3. **Security Scanning**
   - Trivy vulnerability scanning
   - Safety dependency checking
   - SARIF report generation

4. **Docker Build**
   - Container build and caching
   - Container health checks

5. **Infrastructure Validation**
   - Terraform format checking
   - Terraform validation

6. **Deployment** (main branch only)
   - Automated staging deployment
   - Manual approval for production
   - Release creation with changelog

### Running CI/CD Locally

```bash
# Install CI tools
pip install black flake8 isort bandit safety pytest pytest-cov

# Run code quality checks
make lint

# Run tests
make test

# Build Docker image
make docker-build
```

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

- [ ] Export journal entries to PDF
- [ ] Analytics dashboard for mood/energy trends
- [ ] Mobile app with offline sync
- [ ] Email notifications for journal reminders
- [ ] Journal entry templates
- [ ] Multi-language support
- [ ] Vault integration for secret management
- [ ] API endpoints for external integrations
- [ ] Webhook support for automation
- [ ] Advanced search and filtering

## 👨‍💻 About This Project

This project demonstrates:
- **Full-stack development** with Python/Flask
- **Cloud architecture** with AWS services
- **DevOps practices** with Docker and Terraform
- **Security best practices** for web applications
- **Modern UI/UX** design principles

Perfect for showcasing SRE/Senior Python Engineer capabilities including infrastructure automation, cloud services integration, and production-ready application development. 