# Ocean Data Dashboard - Requirements Specification

## Project Overview

**Status:** Open Source | **Maintainer:** Solo | **Budget:** Limited

A fully dockerized, real-time oceanographic data visualization platform that ingests, stores, and displays ocean metrics from leading open-science providers (NOAA ERDDAP, Copernicus Marine Service, NASA OceanColor).

**Target Platform:** AWS with Terraform Infrastructure as Code
**Data Ingestion:** AWS Lambda (serverless, cost-effective)
**Database:** Self-managed PostgreSQL on EC2 (budget-optimized)

**Architecture:** AWS-first with Terraform IaC, serverless ingestion, self-managed infrastructure.

---

## 1. Functional Requirements

### 1.1 Data Ingestion Pipeline (REQ-001)
| Attribute | Specification |
|-----------|---------------|
| **ID** | REQ-001 |
| **Description** | Serverless ETL pipeline to fetch oceanographic data from external APIs |
| **Priority** | Must Have |
| **Data Sources** | NOAA ERDDAP, Copernicus Marine Service, NASA OceanColor |
| **Data Types** | Temperature, Salinity, Currents, Chlorophyll-a |
| **Frequency** | Configurable (default: every 6 hours) |
| **Trigger** | AWS EventBridge (CloudWatch Events) → Lambda invocation |
| **Compute** | AWS Lambda (Python runtime) |

**Lambda Architecture:**
```
EventBridge (Schedule) → Lambda Function → Data Sources → PostgreSQL
```

**Acceptance Criteria:**
- [ ] Lambda function successfully fetches data from at least 2 data sources
- [ ] Handles API timeouts gracefully with exponential backoff (max 3 retries)
- [ ] Lambda execution role has minimal IAM permissions (least privilege)
- [ ] Failed executions logged to CloudWatch Logs with structured JSON
- [ ] Dead Letter Queue (SQS) for failed invocations
- [ ] Stores raw and processed data separately (S3 raw, PostgreSQL processed)

### 1.2 Serverless Processing (REQ-002)
| Attribute | Specification |
|-----------|---------------|
| **ID** | REQ-002 |
| **Description** | AWS Lambda-based async processing for data ingestion |
| **Priority** | Must Have |
| **Technology** | AWS Lambda + EventBridge |
| **Tasks** | Data fetch, transformation, storage to PostgreSQL |

**Lambda Specifications:**
- **Runtime:** Python 3.11+
- **Memory:** 512MB (adjustable based on data volume)
- **Timeout:** 5 minutes (15 min max)
- **Concurrency:** Reserved concurrency of 5 (prevent database overwhelm)
- **Layers:** Custom layer for scientific Python (pandas, xarray, netCDF4)

**Acceptance Criteria:**
- [ ] Lambda executes without blocking API requests
- [ ] Failed invocations retry via EventBridge retry policy
- [ ] CloudWatch Logs capture execution details and errors
- [ ] Cold start optimized (provisioned concurrency optional for later)
- [ ] Function packaged and deployed via Terraform

### 1.3 REST API (REQ-003)
| Attribute | Specification |
|-----------|---------------|
| **ID** | REQ-003 |
| **Description** | RESTful API exposing cleaned time-series datasets |
| **Priority** | Must Have |
| **Framework** | Django REST Framework |
| **Deployment** | AWS EC2 (t3.micro/t3.small) in Docker container |
| **Documentation** | Auto-generated via drf-spectacular (OpenAPI/Swagger) |

**Required Endpoints:**
- `GET /api/v1/measurements/` - List all measurements
- `GET /api/v1/measurements/?variable=temperature&start=2024-01-01&end=2024-01-31` - Filtered data
- `GET /api/v1/sources/` - Available data sources
- `GET /api/v1/stats/` - Data availability statistics
- `GET /api/v1/health/` - Health check endpoint (for ALB)

**Acceptance Criteria:**
- [ ] All endpoints return JSON with proper HTTP status codes
- [ ] Pagination implemented (default: 50 items/page)
- [ ] CORS configured for frontend access
- [ ] Rate limiting: 100 requests/minute per IP (Django Ratelimit)
- [ ] API serves static files via WhiteNoise (no nginx required initially)

### 1.4 Interactive Visualizations (REQ-004)
| Attribute | Specification |
|-----------|---------------|
| **ID** | REQ-004 |
| **Description** | Frontend dashboard with real-time charts using RadixUI primitives |
| **Priority** | Must Have |
| **Framework** | Next.js 14+ with TypeScript |
| **UI Components** | shadcn/ui (built on RadixUI primitives) |
| **Chart Library** | Recharts or Tremor (built on Radix) |
| **Styling** | Tailwind CSS |

**Required shadcn/ui Components:**
- `Select` - Date range and variable selection
- `DatePicker` - Custom date range picker
- `Card` - Data display containers
- `Tabs` - Variable switching
- `Dialog` - Data source information modal
- `Skeleton` - Loading states
- `Tooltip` - Chart hover information
- `DropdownMenu` - Navigation and options

**Required Charts:**
- Time-series line chart (Temperature over time)
- Multi-variable comparison chart
- Regional data heatmap (simplified, MVP phase)

**Acceptance Criteria:**
- [ ] All UI components use RadixUI primitives via shadcn/ui
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Charts update without page refresh
- [ ] Date range selector with presets (last 7d, 30d, 90d)
- [ ] Variable type toggle (Temperature, Salinity, Currents)
- [ ] Accessible (WCAG 2.1 AA compliance via Radix)

### 1.5 Data Filtering (REQ-005)
| Attribute | Specification |
|-----------|---------------|
| **ID** | REQ-005 |
| **Description** | Filter data by date, variable type, and location |
| **Priority** | Must Have |
| **UI Framework** | shadcn/ui Select, DatePicker components |

**Acceptance Criteria:**
- [ ] Date range filtering (start date, end date) via DatePicker
- [ ] Variable type dropdown (Temperature, Salinity, Currents, Chlorophyll) via Select
- [ ] Region selection (initially: simple dropdown with predefined regions)
- [ ] Filters applied via URL query parameters (sharable links)

### 1.6 Monitoring & Logging (REQ-006)
| Attribute | Specification |
|-----------|---------------|
| **ID** | REQ-006 |
| **Description** | AWS-native monitoring for pipeline health |
| **Priority** | Must Have |
| **Tools** | CloudWatch Logs, CloudWatch Metrics, CloudWatch Alarms |

**Monitoring Setup:**
| Component | Metric | Alarm |
|-----------|--------|-------|
| Lambda | Error rate > 5% | SNS → Email |
| Lambda | Duration > 30s | SNS → Email |
| EC2 (API) | CPU > 80% | SNS → Email |
| PostgreSQL | Storage > 80% | SNS → Email |
| Application | 5xx errors > 1% | SNS → Email |

**Acceptance Criteria:**
- [ ] All Lambda invocations logged to CloudWatch
- [ ] Structured JSON logging format (correlation IDs)
- [ ] CloudWatch Alarms for critical failures
- [ ] SNS topic for email notifications
- [ ] CloudWatch Dashboard for at-a-glance health (optional)
- [ ] Django Admin shows last ingestion status

---

## 2. Non-Functional Requirements

### 2.1 Dockerization (NFR-001)
| Attribute | Specification |
|-----------|---------------|
| **ID** | NFR-001 |
| **Description** | 100% containerized development and local deployment |
| **Priority** | Must Have |

**Requirements:**
- All services containerized for local development
- Single `docker-compose up` command for local development
- Multi-stage Docker builds for production optimization
- Health checks on all containers
- Named volumes for data persistence
- **Note:** Production uses AWS Lambda (not containerized there)

**Local Stack:**
- PostgreSQL 15 (matches EC2 production setup)
- Redis (for local caching, optional in production)
- Django backend (dev server)
- Next.js frontend (dev server)

### 2.2 Database (NFR-002)
| Attribute | Specification |
|-----------|---------------|
| **ID** | NFR-002 |
| **Description** | Self-managed PostgreSQL on EC2 |
| **Priority** | Must Have |
| **Version** | 15+ |
| **Deployment** | EC2 t3.micro or t3.small (not RDS) |

**Rationale for EC2 over RDS:**
- Cost: ~$8-15/month EC2 vs ~$13-25/month RDS (t3.micro)
- Control: Direct access to PostgreSQL configuration
- Learning: Better understanding of database operations

**Requirements:**
- PostgreSQL installed via Docker on dedicated EC2 instance
- Automated daily backups to S3 (via cron + pg_dump)
- EBS volume for data persistence (gp3, 20GB minimum)
- Security group allowing access only from API server
- Database migrations via Django (local dev and production)

**EC2 Database Specifications:**
- **Instance:** t3.micro (2 vCPU, 1GB RAM) or t3.small
- **Storage:** 20GB EBS gp3 (expandable to 100GB)
- **Backup:** Daily to S3 (lifecycle policy: 30 days)
- **Monitoring:** CloudWatch custom metrics for storage

### 2.3 Infrastructure as Code (NFR-003)
| Attribute | Specification |
|-----------|---------------|
| **ID** | NFR-003 |
| **Description** | Terraform-managed AWS infrastructure |
| **Priority** | Must Have |
| **Tool** | Terraform 1.6+ with AWS provider |

**Terraform Modules:**
```
infra/terraform/
├── modules/
│   ├── vpc/              # Networking
│   ├── ec2/              # Application and Database servers
│   ├── lambda/           # Ingestion function
│   ├── eventbridge/      # Scheduling
│   ├── s3/               # Storage and backups
│   ├── iam/              # Roles and policies
│   └── cloudwatch/       # Monitoring
├── environments/
│   ├── dev/
│   └── prod/
└── main.tf
```

**Resources Managed:**
- [ ] VPC with public and private subnets
- [ ] Internet Gateway and NAT Gateway (for Lambda in private subnet)
- [ ] EC2 instances (API server, Database server)
- [ ] Security Groups (least privilege)
- [ ] Lambda function and EventBridge rule
- [ ] S3 buckets (raw data, backups)
- [ ] IAM roles and policies
- [ ] CloudWatch Log Groups and Alarms
- [ ] SNS topics for notifications
- [ ] Route 53 records (optional, can use IP initially)

### 2.4 Security (NFR-004)
| Attribute | Specification |
|-----------|---------------|
| **ID** | NFR-004 |
| **Priority** | Must Have |

**Requirements:**
- No secrets in code (AWS Systems Manager Parameter Store or env vars)
- Django SECRET_KEY in Parameter Store
- Database credentials in Parameter Store
- IAM roles for Lambda (no hardcoded credentials)
- Security groups: database only accessible from API server
- EC2 instances: key pair authentication (disable password auth)
- HTTPS via Let's Encrypt (certbot) or ACM + ALB
- CORS properly configured (whitelist only frontend domain)
- Dependencies scanned via Dependabot
- Terraform state in S3 with encryption

### 2.5 Performance (NFR-005)
| Attribute | Specification |
|-----------|---------------|
| **ID** | NFR-005 |
| **Priority** | Should Have |

**Requirements:**
- API response time < 500ms for filtered queries
- Frontend Time to Interactive < 3s
- Database queries optimized (use `select_related`, `prefetch_related`)
- Static assets served with caching headers (WhiteNoise + CloudFront)
- Lambda cold start < 3s (mitigated by EventBridge scheduling)

### 2.6 Scalability (NFR-006)
| Attribute | Specification |
|-----------|---------------|
| **ID** | NFR-006 |
| **Description** | Design for single-node with scaling path |
| **Priority** | Could Have |

**Current:**
- Single EC2 for API, single EC2 for database
- Lambda auto-scales (concurrency limits set)

**Future Path:**
- API: Move to ECS Fargate or Elastic Beanstalk
- Database: Migrate to RDS when EC2 becomes limiting
- Frontend: CloudFront + S3 (static hosting)

---

## 3. AWS Deployment Architecture

### 3.1 Production Architecture
**Estimated Cost:** $20-40/month

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                            │
│  ┌──────────────┐                                           │
│  │  EventBridge │──(schedule)──┐                            │
│  │   (6 hours)  │              │                            │
│  └──────────────┘              ▼                            │
│  ┌─────────────────────────────────────┐                    │
│  │         Lambda (Ingestion)          │                    │
│  │  ┌────────┐  ┌────────┐  ┌───────┐ │                    │
│  │  │ NOAA   │  │Copernic│  │ NASA  │ │                    │
│  │  │ ERDDAP │  │ Marine │  │ Ocean │ │                    │
│  │  └────┬───┘  └───┬────┘  └───┬───┘ │                    │
│  │       └──────────┴───────────┘     │                    │
│  │                   │                 │                    │
│  │                   ▼                 │                    │
│  │            ┌──────────┐            │                    │
│  │            │Transform │────────────┼────┐              │
│  │            │ & Load   │            │    │              │
│  │            └──────────┘            │    │              │
│  └─────────────────────────────────────┘    │              │
│                                             ▼              │
│  ┌─────────────┐      ┌──────────────────────────────┐     │
│  │     S3      │      │      EC2 (Database)        │     │
│  │  (Raw Data) │      │  ┌────────────────────────┐ │     │
│  │             │      │  │   PostgreSQL 15        │ │     │
│  └─────────────┘      │  │   - Port 5432          │ │     │
│                       │  │   - EBS 20GB           │ │     │
│  ┌─────────────┐      │  │   - Daily backups to S3│ │     │
│  │  CloudWatch │      │  └────────────────────────┘ │     │
│  │  (Logs/Alarms)     └──────────────────────────────┘     │
│  └─────────────┘              ▲                           │
│                               │                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              EC2 (Application/API)                   │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Docker Compose Stack:                       │   │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌──────────────┐ │   │   │
│  │  │  │ Django  │  │ Next.js │  │ WhiteNoise   │ │   │   │
│  │  │  │ API     │  │ Frontend│  │ (static)     │ │   │   │
│  │  │  └────┬────┘  └────┬────┘  └──────────────┘ │   │   │
│  │  │       └───────────┬┘                        │   │   │
│  │  │                   │                         │   │   │
│  │  │              ┌────┴────┐                     │   │   │
│  │  │              │  Nginx  │                     │   │   │
│  │  │              │(reverse)│                     │   │   │
│  │  │              └────┬────┘                     │   │   │
│  │  └───────────────────┼──────────────────────────┘   │   │
│  └──────────────────────┼───────────────────────────────┘   │
│                         │                                   │
│  ┌─────────────┐       │                                   │
│  │   Route 53  │───────┘                                   │
│  │   (DNS)     │                                           │
│  └─────────────┘       ┌─────────────┐                     │
│                        │  CloudFront │ (optional)         │
│                        │    CDN      │                    │
│                        └─────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Cost Breakdown (Monthly)

| Service | Component | Cost |
|---------|-----------|------|
| **EC2** | t3.micro API server (730 hrs) | ~$8.50 |
| **EC2** | t3.micro Database server (730 hrs) | ~$8.50 |
| **EBS** | 20GB gp3 × 2 volumes | ~$3.20 |
| **S3** | 10GB storage + requests | ~$0.50 |
| **Lambda** | 1M requests + 512MB RAM | ~$0.20 (Free tier covers) |
| **CloudWatch** | Logs and metrics | ~$1.00 |
| **Data Transfer** | 100GB outbound | ~$9.00 |
| **TOTAL** | | **~$30-35/month** |

**Cost Optimization:**
- Use Savings Plans for EC2 (1-year, ~40% discount)
- S3 Intelligent-Tiering for old backups
- Consider Spot instances for non-critical workloads

### 3.3 Terraform State Management

**S3 Backend Configuration:**
```hcl
terraform {
  backend "s3" {
    bucket         = "ocean-dashboard-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"  # For state locking
  }
}
```

---

## 4. Frontend: RadixUI + shadcn/ui Specification

### 4.1 Component Requirements

**Navigation:**
- `shadcn/ui NavigationMenu` - Main navigation
- `shadcn/ui DropdownMenu` - User actions (future)

**Data Selection:**
- `shadcn/ui Select` - Variable type, region selection
- `shadcn/ui DatePicker` - Date range selection (built on Radix Popover)
- `shadcn/ui Button` - Apply filters, actions

**Data Display:**
- `shadcn/ui Card` - Metric cards, chart containers
- `shadcn/ui Tabs` - Switch between variables
- `shadcn/ui Skeleton` - Loading states for charts
- `shadcn/ui Tooltip` - Chart hover details

**Feedback:**
- `shadcn/ui Toast` (via Sonner) - Notifications
- `shadcn/ui Alert` - Error messages
- `shadcn/ui Dialog` - Data source information, settings

**Charts:**
- Recharts (integrates well with shadcn)
- OR Tremor (built on Radix, opinionated components)

### 4.2 shadcn/ui Installation & Setup

```bash
# Initialize shadcn/ui in Next.js project
npx shadcn-ui@latest init

# Install required components
npx shadcn-ui@latest add button card select tabs tooltip skeleton datepicker
npx shadcn-ui@latest add navigation-menu dropdown-menu dialog alert

# Install chart library
npm install recharts
# OR
npm install @tremor/react
```

### 4.3 Theming

- **Base color:** Slate or Zinc
- **CSS Variables:** Configure in `tailwind.config.ts`
- **Dark mode:** Supported via next-themes
- **Custom colors:** Ocean-themed (blues, teals) as CSS variables

---

## 5. Lambda Ingestion Function Specification

### 5.1 Function Structure

```python
# lambda_function.py
import json
import boto3
import requests
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """
    Triggered by EventBridge schedule.
    Fetches data from configured sources and stores in PostgreSQL.
    """
    # 1. Get configuration from Parameter Store
    # 2. Fetch data from NOAA ERDDAP
    # 3. Transform and validate
    # 4. Store in PostgreSQL
    # 5. Return success metrics
    pass
```

### 5.2 Lambda Layer Requirements

**Custom Lambda Layer:**
```
python-science-layer/
├── python/
│   ├── pandas/
│   ├── numpy/
│   ├── xarray/
│   ├── netCDF4/
│   └── psycopg2-binary/
```

**Build process:**
```bash
# Use Docker to build compatible layer
docker run -v "$PWD":/var/task "public.ecr.aws/sam/build-python3.11:latest-x86_64" \
    /bin/sh -c "pip install -r requirements.txt -t python/lib/python3.11/site-packages/"
zip -r lambda-layer.zip python
```

### 5.3 EventBridge Schedule

```json
{
  "ScheduleExpression": "rate(6 hours)",
  "Name": "ocean-data-ingestion-schedule",
  "Description": "Trigger ocean data ingestion every 6 hours",
  "State": "ENABLED",
  "Target": {
    "Arn": "arn:aws:lambda:REGION:ACCOUNT:function:ocean-ingestion",
    "Id": "ocean-ingestion-target"
  }
}
```

---

## 6. Single Maintainer Considerations

### 6.1 Terraform Workflow

**Local Development:**
```bash
# Initialize
cd infra/terraform
terraform init

# Plan changes
terraform plan -var-file=environments/dev.tfvars

# Apply (manual approval recommended for production)
terraform apply -var-file=environments/dev.tfvars
```

**CI/CD Integration:**
- GitHub Actions for `terraform plan` on PRs
- Manual approval for `terraform apply` on main

### 6.2 Maintenance Burden

| Task | Frequency | Tool |
|------|-----------|------|
| Dependency updates | Monthly | Dependabot + manual |
| Terraform provider updates | Quarterly | terraform init -upgrade |
| Security patches | As needed | AWS Security Hub alerts |
| Database backups | Daily | Automated via cron |
| Cost review | Monthly | AWS Cost Explorer |
| Log rotation | Weekly | logrotate on EC2 |

### 6.3 Documentation Requirements

- [ ] README with quick start (exists)
- [ ] `infra/terraform/README.md` - Infrastructure setup
- [ ] `infra/terraform/DEPLOYMENT.md` - Step-by-step deployment
- [ ] `docs/TROUBLESHOOTING.md` - Common AWS issues
- [ ] `docs/LAMBDA.md` - Ingestion function development
- [ ] Environment variable reference (all sources)

---

## 7. Open Source Requirements

### 7.1 Licensing
- **Code:** MIT License
- **Data:** Attribute NOAA, Copernicus, NASA sources

### 7.2 Repository Hygiene
- [ ] Conventional Commits
- [ ] CHANGELOG.md
- [ ] Tagged releases (v1.0.0, etc.)
- [ ] Dependabot enabled
- [ ] Terraform-docs for infrastructure documentation

---

## 8. Data Retention & Storage

| Data Type | Retention | Storage |
|-----------|-----------|---------|
| Raw API responses | 30 days | S3 Standard-IA |
| Processed measurements | 1 year | PostgreSQL on EC2 |
| Aggregated statistics | Indefinite | PostgreSQL |
| Backups | 30 days | S3 Glacier (after 7 days) |
| Application logs | 30 days | CloudWatch Logs |

**S3 Lifecycle Policy:**
- Days 0-7: S3 Standard
- Days 8-30: S3 Standard-IA
- After 30 days: Delete or move to Glacier

---

## 9. MVP Success Criteria

1. [ ] **Data Pipeline:** Lambda successfully ingests temperature data from NOAA ERDDAP
2. [ ] **API:** REST endpoint serves time-series data with date filtering
3. [ ] **Frontend:** Displays interactive temperature chart using RadixUI/shadcn components
4. [ ] **Automation:** EventBridge triggers Lambda every 6 hours
5. [ ] **Deployment:** Terraform provisions EC2 (API + Database) on AWS
6. [ ] **Monitoring:** CloudWatch alarms notify on ingestion failures
7. [ ] **Documentation:** README allows contributor to deploy in < 1 hour

---

## 10. Future Enhancements (Post-MVP)

- [ ] Additional data sources (ARGO, satellite)
- [ ] RDS migration when EC2 limits reached
- [ ] ECS Fargate for API (remove single EC2 point of failure)
- [ ] CloudFront for CDN
- [ ] User accounts and saved queries
- [ ] Real-time updates via WebSocket

---

## 11. Technical Constraints

| Constraint | Rationale |
|------------|-----------|
| Python 3.11+ | Lambda runtime support, performance |
| Django 4.2+ | LTS version |
| Next.js 14+ | App Router, performance |
| PostgreSQL 15 | Compatibility, performance |
| Terraform 1.6+ | Stable, AWS provider maturity |
| shadcn/ui | RadixUI primitives, accessibility, theming |
| AWS Lambda | Serverless, pay-per-use, auto-scale |
| EC2 (not RDS) | Cost savings, learning opportunity |

---

## 12. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Lambda timeout on large datasets | Medium | High | Pagination, smaller batch sizes |
| EC2 database corruption | Low | High | Daily backups, EBS snapshots |
| Terraform state corruption | Low | High | S3 backend with versioning |
| Lambda layer size limits | Medium | Medium | Optimize dependencies, use container image if needed |
| Data source API changes | Medium | High | Versioned API clients, error alerting |
| AWS costs exceeding budget | Medium | Medium | Billing alerts, Cost Explorer monitoring |

---

## Appendix A: Environment Variables Reference

### Lambda Environment Variables
```
DB_HOST=ec2-xx-xx-xx-xx.compute-1.amazonaws.com
DB_PORT=5432
DB_NAME=oceandb
DB_USER=oceanuser
DB_PASSWORD=ssm:/ocean-dashboard/db-password
NOAA_API_BASE_URL=https://coastwatch.pfeg.noaa.gov/erddap
S3_RAW_BUCKET=ocean-raw-data-bucket
LOG_LEVEL=INFO
```

### EC2 Application Environment (via Parameter Store)
```
DATABASE_URL=postgresql://oceanuser:password@db-server:5432/oceandb
DJANGO_SECRET_KEY=ssm:/ocean-dashboard/django-secret
DJANGO_DEBUG=False
ALLOWED_HOSTS=your-domain.com
SENTRY_DSN=optional
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-domain.com/api
NEXT_PUBLIC_APP_NAME=Ocean Data Dashboard
```

---

## Appendix B: Terraform Variable Reference

```hcl
# environments/prod.tfvars
aws_region      = "us-east-1"
environment     = "production"

# EC2 Configuration
api_instance_type    = "t3.micro"
db_instance_type     = "t3.micro"
key_name             = "ocean-dashboard-key"

# Database
db_name              = "oceandb"
db_username          = "oceanuser"
db_allocated_storage = 20

# Lambda
lambda_memory_size   = 512
lambda_timeout       = 300

# S3
raw_data_bucket_name = "ocean-dashboard-raw-data"

# Notifications
alert_email          = "admin@kuroshio-lab.com"
```

---

**Document Version:** 2.0
**Last Updated:** 2026-02-18
**Author:** Solo Maintainer
**Status:** AWS-Ready Specification
