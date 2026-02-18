# infra/CLAUDE.md

Infrastructure for deploying Ocean Data Dashboard to AWS. **Cost-conscious, serverless-first, single EC2 instance.**

## Architecture Overview

```
Route53 (global infra)
    └── dashboard.kuroshio-lab.com
        ↓
EC2 Instance (t3.small, $10-15/month)
├── Docker Container: Backend (Django + Celery scheduler stub)
├── Docker Container: Frontend (Next.js)
└── Docker Container: PostgreSQL (30-day rolling data)
        ↓
Lambda Functions (serverless, pay-per-invocation)
├── lambda/fetch_noaa_data (triggered via CloudWatch Events)
├── lambda/fetch_copernicus_data
├── lambda/fetch_chlorophyll_data
└── lambda/cleanup_observations (monthly)
        ↓
Secrets Manager (API keys, DB passwords)
        ↓
S3 (shared with global infra for assets)
        ↓
CloudWatch (logs, monitoring, cost alarms)
```

## Cost Estimate

**Monthly AWS Costs** (estimated):
- EC2 (t3.small, 730 hours): ~$12-15
- Lambda (async tasks, ~200 invocations/month): ~$0-2
- Secrets Manager (2 secrets): ~$1
- CloudWatch Logs: ~$0-2
- Data Transfer (minimal): ~$0-1
- Route53 (managed by global infra): ~$0
- **Total**: ~$15-20/month

## Local Development (Docker Compose)

Everything runs locally before deploying to AWS:

```bash
cd /repo/root

# Start all services
docker-compose up -d

# Services:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

**docker-compose.yml structure:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://ocean:oceanpass@postgres:5432/oceandb
      REDIS_URL: redis://redis:6379/0
      DJANGO_DEBUG: "True"
      AWS_REGION: eu-west-3
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: oceandb
      POSTGRES_USER: ocean
      POSTGRES_PASSWORD: oceanpass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

Note: `.env` files should NOT be committed. Use `docker-compose.override.yml` for local overrides.

## AWS Deployment: Terraform

### Directory Structure

```
infra/
├── terraform/
│   ├── backend.tf              # State config (S3 + DynamoDB)
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Export values
│   ├── main.tf                 # AWS provider
│   ├── ec2.tf                  # EC2 instance + security groups
│   ├── lambda.tf               # Lambda functions for async tasks
│   ├── rds-alternative.tf      # (Optional) Self-hosted DB notes
│   ├── dns.tf                  # Route53 integration
│   ├── secrets.tf              # Secrets Manager
│   └── monitoring.tf           # CloudWatch alarms
├── lambda/
│   ├── fetch_noaa.py           # Async data fetching
│   ├── fetch_copernicus.py
│   ├── fetch_chlorophyll.py
│   └── cleanup.py              # Monthly data cleanup
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── entrypoint.sh
└── README.md                   # Deployment guide
```

### Step 1: Prerequisites

```bash
# Install tools
brew install terraform aws-cli  # macOS
apt install terraform awscli    # Linux

# Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, region (eu-west-3), output format (json)

# Verify credentials
aws sts get-caller-identity
```

### Step 2: Initialize Terraform Backend

ONE TIME ONLY - Set up S3 + DynamoDB for state management:

```bash
cd infra/terraform

# The backend.tf should reference the global kuroshio-lab state:
# terraform {
#   backend "s3" {
#     bucket         = "kuroshio-lab-terraform-state"
#     key            = "ocean-dashboard/terraform.tfstate"
#     region         = "eu-west-3"
#     dynamodb_table = "terraform-state-lock"
#     encrypt        = true
#   }
# }

# This assumes the global infra has already created the S3 bucket + DynamoDB table
# If not, see docs in the global infra repo
```

### Step 3: Create Terraform Variables

Create `infra/terraform/terraform.tfvars`:

```hcl
app_name       = "ocean-dashboard"
environment    = "production"
aws_region     = "eu-west-3"
instance_type  = "t3.small"
domain_name    = "dashboard.kuroshio-lab.com"
docker_image_backend  = "ocean-dashboard:backend-latest"
docker_image_frontend = "ocean-dashboard:frontend-latest"
```

### Step 4: Deploy Infrastructure

```bash
cd infra/terraform

# Initialize (downloads Terraform modules)
terraform init

# Preview changes
terraform plan

# Apply infrastructure (creates EC2, Lambda, security groups, etc.)
terraform apply
# Type 'yes' when prompted

# Get outputs (EC2 IP, Lambda ARNs, etc.)
terraform output
```

## EC2 Instance Setup

### Terraform Configuration (ec2.tf)

```hcl
resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type  # t3.small
  key_name      = aws_key_pair.deployer.key_name

  vpc_security_group_ids = [aws_security_group.app.id]

  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

  # User data: Install Docker, pull images, start containers
  user_data = base64encode(file("${path.module}/../docker/entrypoint.sh"))

  tags = {
    Name = "${var.app_name}-server"
  }
}

resource "aws_security_group" "app" {
  name = "${var.app_name}-sg"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allow HTTP from anywhere
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Allow HTTPS from anywhere
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # SSH (restrict to your IP in production!)
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### Docker Entrypoint (infra/docker/entrypoint.sh)

```bash
#!/bin/bash
set -e

# Update system
apt-get update
apt-get install -y docker.io docker-compose-plugin

# Create docker-compose.yml on EC2
cat > /home/ubuntu/docker-compose.yml <<'EOF'
version: '3.8'
services:
  backend:
    image: ${DOCKER_IMAGE_BACKEND}
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      DJANGO_DEBUG: "False"
      DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY}
      AWS_REGION: eu-west-3
    depends_on:
      - postgres
      - redis

  frontend:
    image: ${DOCKER_IMAGE_FRONTEND}
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: https://${DOMAIN_NAME}/api

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: oceandb
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
EOF

# Pull images and start containers
cd /home/ubuntu
docker-compose up -d
```

## Lambda Functions (Async Tasks)

### Architecture

Instead of Celery workers running 24/7, use Lambda for periodic tasks:

```
CloudWatch Events (cron)
    ↓ (every 6 hours)
Lambda Function (fetch_noaa_data)
    ↓ (async HTTP request to NOAA)
EC2 Backend (save to PostgreSQL)
    ↓ (invalidate cache)
Redis
```

### Terraform Configuration (lambda.tf)

```hcl
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda"
  output_path = "${path.module}/../lambda.zip"
}

resource "aws_lambda_function" "fetch_noaa" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = "${var.app_name}-fetch-noaa"
  role          = aws_iam_role.lambda_role.arn
  handler       = "fetch_noaa.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60

  environment {
    variables = {
      API_URL = "https://${var.domain_name}/api"
      BACKEND_SECRET = aws_secretsmanager_secret.api_key.arn
    }
  }
}

resource "aws_cloudwatch_event_rule" "fetch_noaa_schedule" {
  name                = "${var.app_name}-fetch-noaa"
  description         = "Fetch NOAA data every 6 hours"
  schedule_expression = "cron(0 */6 * * ? *)"  # Every 6 hours
}

resource "aws_cloudwatch_event_target" "fetch_noaa_target" {
  rule      = aws_cloudwatch_event_rule.fetch_noaa_schedule.name
  target_id = aws_lambda_function.fetch_noaa.id
  arn       = aws_lambda_function.fetch_noaa.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fetch_noaa.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.fetch_noaa_schedule.arn
}
```

### Lambda Function (lambda/fetch_noaa.py)

```python
import json
import requests
import boto3
from datetime import datetime, timedelta

secretsmanager = boto3.client('secretsmanager')

def lambda_handler(event, context):
    """Fetch NOAA data and POST to backend."""

    try:
        # Get backend API key from Secrets Manager
        secret = secretsmanager.get_secret_value(SecretId='ocean-dashboard-api-key')
        api_key = json.loads(secret['SecretString'])['key']

        # Fetch from NOAA
        noaa_data = fetch_noaa_api()

        # POST to backend ingestion endpoint
        response = requests.post(
            'https://dashboard.kuroshio-lab.com/api/observations/ingest/',
            json=noaa_data,
            headers={'Authorization': f'Bearer {api_key}'}
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'records': len(noaa_data)})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def fetch_noaa_api():
    """Fetch data from NOAA ERDDAP."""
    url = "https://oceanwatch.sci.gsfc.nasa.gov/api/..."
    response = requests.get(url)
    response.raise_for_status()
    return normalize_to_observations(response.json())

def normalize_to_observations(raw_data):
    """Transform NOAA format to app format."""
    observations = []
    for record in raw_data:
        observations.append({
            'location_id': map_location(record['lat'], record['lon']),
            'timestamp': record['time'],
            'value': record['temperature'],
            'quality_flag': 'good',
            'source': 'NOAA'
        })
    return observations
```

**Key pattern**: Lambda is stateless, fetches data, POSTs to backend. Backend saves to database.

## Secrets Management (AWS Secrets Manager)

### Terraform Configuration (secrets.tf)

```hcl
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.app_name}/db-password"
  recovery_window_in_days = 7  # Allow recovery for 7 days
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = "ocean"
    password = random_password.db.result
    host     = aws_instance.app_server.private_ip
    port     = 5432
    dbname   = "oceandb"
  })
}

resource "aws_secretsmanager_secret" "api_key" {
  name = "${var.app_name}/api-key"
}

# Manually set via AWS console or:
# aws secretsmanager put-secret-value --secret-id ocean-dashboard/api-key --secret-string '{"key":"your-secret-key"}'
```

### Accessing Secrets in Backend

```python
# backend/core/settings.py
import boto3
import json

def get_secret(secret_name):
    """Fetch secret from AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name='eu-west-3')
    try:
        secret = client.get_secret_value(SecretId=secret_name)
        return json.loads(secret['SecretString'])
    except Exception as e:
        print(f"Error fetching secret: {e}")
        return None

if os.getenv('ENVIRONMENT') == 'production':
    db_secret = get_secret('ocean-dashboard/db-password')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_secret['dbname'],
            'USER': db_secret['username'],
            'PASSWORD': db_secret['password'],
            'HOST': db_secret['host'],
            'PORT': db_secret['port'],
        }
    }
```

## Route53 DNS Integration

### Terraform Configuration (dns.tf)

```hcl
# Reference the global hosted zone
data "aws_route53_zone" "main" {
  name = "kuroshio-lab.com"
  # This zone is managed by the global infra repo
}

# Create A record for this app
resource "aws_route53_record" "app" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "dashboard.kuroshio-lab.com"
  type    = "A"
  ttl     = 300
  records = [aws_instance.app_server.public_ip]
}

# Optional: API subdomain
resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "api.dashboard.kuroshio-lab.com"
  type    = "A"
  ttl     = 300
  records = [aws_instance.app_server.public_ip]
}
```

## Monitoring & Logging (CloudWatch)

### Application Logs

All Docker containers send logs to CloudWatch:

```yaml
# docker-compose.yml (EC2)
services:
  backend:
    logging:
      driver: awslogs
      options:
        awslogs-group: /ocean-dashboard/backend
        awslogs-region: eu-west-3
        awslogs-stream-prefix: ecs
```

### CloudWatch Alarms (Terraform)

```hcl
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ocean-dashboard/backend"
  retention_in_days = 7  # Free tier: 7 days retention
}

resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.app_name}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ErrorCount"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_sns_topic" "alerts" {
  name = "${var.app_name}-alerts"
}

# Subscribe email to topic (set via AWS console)
```

### Manual Monitoring

```bash
# View backend logs
aws logs tail /ocean-dashboard/backend --follow

# View Lambda logs
aws logs tail /aws/lambda/ocean-dashboard-fetch-noaa --follow

# Check EC2 instance status
aws ec2 describe-instance-status --instance-ids i-xxxxx --region eu-west-3
```

## Deployment Workflow

### 1. Local Testing (docker-compose)

```bash
cd /repo/root
docker-compose up -d
# Test at http://localhost:3000
docker-compose down
```

### 2. Build and Push Docker Images

```bash
# Login to ECR or Docker Hub
aws ecr get-login-password --region eu-west-3 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.eu-west-3.amazonaws.com

# Build and push
docker build -t ocean-dashboard:backend-latest ./backend
docker tag ocean-dashboard:backend-latest 123456789.dkr.ecr.eu-west-3.amazonaws.com/ocean-dashboard:backend-latest
docker push 123456789.dkr.ecr.eu-west-3.amazonaws.com/ocean-dashboard:backend-latest

# Repeat for frontend
```

### 3. Deploy Infrastructure

```bash
cd infra/terraform
terraform plan
terraform apply
```

### 4. SSH into EC2 and Verify

```bash
ssh -i ~/.ssh/ocean-dashboard.pem ubuntu@dashboard.kuroshio-lab.com

# Check docker-compose status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# SSH exit
exit
```

### 5. Verify DNS

```bash
# Wait 1-5 minutes for DNS propagation
nslookup dashboard.kuroshio-lab.com

# Test frontend
curl https://dashboard.kuroshio-lab.com

# Test API
curl https://dashboard.kuroshio-lab.com/api/locations/
```

## Environment Variables

**Production (.env on EC2):**
```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<from Secrets Manager>
DATABASE_URL=postgresql://ocean:password@localhost:5432/oceandb
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=https://dashboard.kuroshio-lab.com,https://api.dashboard.kuroshio-lab.com
AWS_REGION=eu-west-3
```

## Cost Optimization Tips

1. **Use Spot Instances** (if tolerable 2-min interruptions)
   - Change `instance_type` to `t3a.small` with spot pricing
   - Save ~70% on compute

2. **Scale Down Database**
   - 30-day retention means aggressive cleanup
   - Monitor database size: `du -sh /var/lib/postgresql/data`

3. **Leverage Lambda for Async**
   - Replace long-running Celery workers with Lambda
   - Pay only for invocation time (~$0.20/million invocations)

4. **Monitor CloudWatch Costs**
   - Log retention: 7 days (free tier)
   - Set budget alerts in AWS Billing

5. **Reserved Capacity** (if committing long-term)
   - 1-year t3.small RI: ~$8/month vs $12-15/month on-demand

## Troubleshooting

### "Terraform state lock timeout"
```bash
# DynamoDB is locked. Either:
# 1. Wait for previous apply to finish
# 2. Or force unlock (dangerous):
terraform force-unlock <lock_id>
```

### "EC2 instance failing to start containers"
```bash
ssh ubuntu@dashboard.kuroshio-lab.com
docker-compose logs backend
# Check CloudWatch logs in AWS console
```

### "Lambda execution failed"
```bash
# Check Lambda logs
aws logs tail /aws/lambda/ocean-dashboard-fetch-noaa --follow

# Test function locally
sam local invoke fetch_noaa -e event.json
```

### "DNS not resolving"
```bash
# DNS propagation takes 1-48 hours
# Check current nameservers:
nslookup -type=NS kuroshio-lab.com

# Should match Route53 nameservers from:
terraform output route53_nameservers  # (in global infra)
```

## Important Notes

### Shared Infrastructure (Global Kuroshio-Lab)
- This repo references `kuroshio-lab-terraform-state` S3 bucket
- Route53 zone `kuroshio-lab.com` is managed by global infra
- S3 bucket for assets (`marinex-assets/ocean-dashboard/`) is shared

### Single EC2 Instance Design
- No auto-scaling (cost-conscious)
- If traffic spikes, manually upgrade instance type
- Monitor CloudWatch CPU metrics
- If avg CPU > 70%, increase to t3.medium (~$20/month)

### Database on EC2
- No automated backups (real-time data is ephemeral)
- Manual snapshots available via: `docker-compose exec postgres pg_dump -U ocean oceandb > backup.sql`
- Keep `.sql` files locally or in S3

### Lambda Cold Starts
- First invocation may be slow (1-3 seconds)
- Acceptable for periodic tasks (data ingestion)
- Not suitable for real-time API responses

---

**Deployment complete!** Dashboard is now live at `https://dashboard.kuroshio-lab.com`

For updates, pull latest code and run `terraform apply` again.

For questions, see backend/CLAUDE.md, frontend/CLAUDE.md, or the global kuroshio-lab/infra documentation.
