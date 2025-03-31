# NICU Fluid Management Web Application - Deployment Guide

This document provides instructions for deploying the NICU Fluid Management Web Application to a production environment.

## Deployment Options

The application can be deployed using several methods:

1. **Google Cloud Platform App Engine** (Recommended)
2. **Docker Container** on any cloud platform
3. **Manual Deployment** on a server

## Prerequisites

- Git
- Python 3.10 or higher
- pip (Python package manager)
- Docker (for container deployment)
- Google Cloud SDK (for GCP deployment)

## Option 1: Deploy to Google Cloud Platform App Engine

### Step 1: Set Up Google Cloud Platform

1. Create a Google Cloud Platform account if you don't have one
2. Create a new project in the Google Cloud Console
3. Enable the App Engine API for your project
4. Install the Google Cloud SDK on your local machine

### Step 2: Configure the Application

1. Clone the repository:
   ```
   git clone <repository-url>
   cd nicu_app
   ```

2. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```

3. Edit the `.env` file to set your production values:
   - Generate a secure random string for `SECRET_KEY`
   - Set up a production database URL (Cloud SQL recommended)
   - Configure admin credentials

### Step 3: Deploy to App Engine

1. Make sure you're authenticated with Google Cloud:
   ```
   gcloud auth login
   ```

2. Set the project:
   ```
   gcloud config set project YOUR_PROJECT_ID
   ```

3. Deploy the application:
   ```
   gcloud app deploy app.yaml
   ```

4. The deployment process will provide a URL where your application is accessible.

## Option 2: Deploy Using Docker

### Step 1: Build the Docker Image

1. Clone the repository:
   ```
   git clone <repository-url>
   cd nicu_app
   ```

2. Build the Docker image:
   ```
   docker build -t nicu-fluid-app .
   ```

### Step 2: Run the Container

1. Create a `.env` file with your production settings
2. Run the container:
   ```
   docker run -d -p 8080:8080 --env-file .env --name nicu-app nicu-fluid-app
   ```

### Step 3: Deploy to Cloud Platforms

#### AWS Elastic Container Service (ECS)

1. Push your Docker image to Amazon ECR
2. Create an ECS cluster and service
3. Configure the task definition to use your image

#### Google Cloud Run

1. Push your Docker image to Google Container Registry
2. Deploy to Cloud Run:
   ```
   gcloud run deploy nicu-app --image gcr.io/YOUR_PROJECT/nicu-fluid-app --platform managed
   ```

## Option 3: Manual Deployment

### Step 1: Set Up the Server

1. Provision a server with Ubuntu 20.04 or newer
2. Install Python 3.10, pip, and required system packages:
   ```
   sudo apt update
   sudo apt install python3.10 python3-pip python3.10-venv nginx
   ```

### Step 2: Deploy the Application

1. Clone the repository:
   ```
   git clone <repository-url>
   cd nicu_app
   ```

2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with production settings

5. Set up Gunicorn as a service:
   ```
   sudo nano /etc/systemd/system/nicu-app.service
   ```

   Add the following content:
   ```
   [Unit]
   Description=NICU Fluid Management App
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/path/to/nicu_app
   Environment="PATH=/path/to/nicu_app/venv/bin"
   EnvironmentFile=/path/to/nicu_app/.env
   ExecStart=/path/to/nicu_app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8080 src.web_server:app

   [Install]
   WantedBy=multi-user.target
   ```

6. Start and enable the service:
   ```
   sudo systemctl start nicu-app
   sudo systemctl enable nicu-app
   ```

7. Configure Nginx as a reverse proxy:
   ```
   sudo nano /etc/nginx/sites-available/nicu-app
   ```

   Add the following content:
   ```
   server {
       listen 80;
       server_name your_domain.com;

       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

8. Enable the site and restart Nginx:
   ```
   sudo ln -s /etc/nginx/sites-available/nicu-app /etc/nginx/sites-enabled
   sudo systemctl restart nginx
   ```

## Monitoring and Maintenance

### Monitoring

The application includes built-in monitoring features:

- Health check endpoints: `/health` and `/health/db`
- Logging to `/app/logs/nicu_app.log`
- Performance monitoring for slow requests

For production, consider integrating with:
- Sentry for error tracking (set `SENTRY_DSN` environment variable)
- New Relic for performance monitoring (set `NEW_RELIC_LICENSE_KEY` environment variable)

### Backups

A backup script is included in `maintenance/backup.sh`. Set up a cron job to run this regularly:

```
# Run backup daily at 2 AM
0 2 * * * /path/to/nicu_app/maintenance/backup.sh
```

### Database Migrations

When updating the application with schema changes:

1. Stop the application
2. Back up the database
3. Apply migrations
4. Restart the application

## Troubleshooting

### Common Issues

1. **Application not starting**:
   - Check logs: `tail -f /app/logs/nicu_app.log`
   - Verify environment variables are set correctly

2. **Database connection errors**:
   - Ensure database credentials are correct
   - Check if database server is running
   - Verify network connectivity to database

3. **Static files not loading**:
   - Check Nginx configuration
   - Verify static files are included in the deployment

### Getting Help

For additional support, please contact the development team.
