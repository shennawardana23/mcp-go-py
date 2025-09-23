# 🚀 AWS Deployment Guide: Lambda & API Gateway

## 📋 Overview

This guide covers deploying MCP-PBA-TUNNEL to AWS using Lambda Functions and API Gateway for a serverless architecture with PostgreSQL database.

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph "AWS Cloud"
        A[API Gateway<br/>REST API] --> B[Lambda Function<br/>FastAPI Application]
        B --> C[PostgreSQL RDS<br/>Database]
        B --> D[Redis ElastiCache<br/>Caching]
        B --> E[CloudWatch<br/>Monitoring]
    end

    subgraph "External Services"
        F[OpenAI API<br/>AI Enhancement] --> B
        G[Anthropic API<br/>Claude Models] --> B
    end

    subgraph "Development"
        H[Local Development<br/>SQLite] --> I[Git Repository<br/>Version Control]
        I --> J[AWS SAM CLI<br/>Deployment]
    end

    J --> A
```

## 📋 Prerequisites

### 1. AWS Account & CLI

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format
```

### 2. AWS SAM CLI

```bash
# Install AWS SAM CLI
curl -Lo aws-sam-cli-linux-x86_64.zip "https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip"
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install

# Verify installation
sam --version
```

### 3. Docker (for building Lambda layers)

```bash
# Install Docker
# Follow instructions at: https://docs.docker.com/get-docker/
docker --version
```

## 🔧 Infrastructure Setup

### 1. VPC Configuration

Before deployment, ensure you have a VPC with:

- 2+ Private Subnets
- 1+ Public Subnet
- Internet Gateway
- NAT Gateway
- Route Tables

### 2. Database Security

- PostgreSQL RDS instance
- Security groups for Lambda access
- Subnet groups for RDS

## 🚀 Deployment Steps

### Step 1: Environment Configuration

Create a `.env` file for your deployment:

```bash
# .env
STACK_NAME=mcp-pba-tunnel
AWS_REGION=us-east-1
STAGE=prod
DB_PASSWORD=your-secure-postgres-password
```

### Step 2: Build Lambda Layer

```bash
# Build Lambda layer dependencies
cd lambda-layer
./build.sh
cd ..
```

### Step 3: Deploy to AWS

```bash
# Deploy using SAM CLI
sam build

sam deploy --guided
# Or with parameters:
sam deploy \
  --template-file template.yaml \
  --stack-name $STACK_NAME \
  --region $AWS_REGION \
  --parameter-overrides \
    StageName=$STAGE \
    DatabaseUrl="postgresql://mcp_user:$DB_PASSWORD@localhost:5432/mcp_pba_tunnel" \
  --capabilities CAPABILITY_IAM
```

### Step 4: Verify Deployment

```bash
# Check deployment status
aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $AWS_REGION

# Get API Gateway URL
API_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $AWS_REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text)

# Test the API
curl -X GET "$API_URL/health"
curl -X POST "$API_URL/api/categories" -H "Content-Type: application/json"
```

## 🔧 Configuration Management

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Required | Yes |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | No |
| `POWERTOOLS_LOGGER` | Enable PowerTools logging | true | No |
| `POWERTOOLS_TRACER` | Enable PowerTools tracing | true | No |
| `REDIS_URL` | Redis connection string for caching | Optional | No |

### Database Configuration

The application uses PostgreSQL for both development and AWS Lambda deployment:

```python
# Development (PostgreSQL)
DATABASE_URL = "postgresql://postgres:password@localhost:5432/mcp_pba_tunnel"

# AWS Lambda (PostgreSQL)
DATABASE_URL = "postgresql://user:password@rds-endpoint:5432/mcp_pba_tunnel"
```

## 🗃️ Database Migration

### Initial Setup

```bash
# Run migrations locally
alembic upgrade head

# In Lambda, migrations run automatically on startup
```

### Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Add user tracking"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current revision
alembic current

# Show migration history
alembic history
```

## 🔐 Security Configuration

### API Gateway Security

```yaml
# In template.yaml
Resources:
  ApiGateway:
    Type: AWS::Serverless::Api
    Properties:
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,X-Amz-Date,Authorization'"
        AllowOrigin: "'*'"
      Auth:
        ApiKeyRequired: false
        DefaultAuthorizer: AWS_IAM
```

### Lambda Security

- **IAM Roles**: Least privilege access
- **VPC**: Private subnet deployment
- **Security Groups**: Restrict database access
- **Environment Variables**: Secure configuration

## 📊 Monitoring & Logging

### CloudWatch Configuration

```python
# Lambda function logging
logger = Logger()
tracer = Tracer()

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info("Processing request")
    # Your code here
```

### Monitoring Metrics

- Lambda execution time
- API Gateway latency
- Database connection pool usage
- Error rates and 4xx/5xx responses
- Memory and CPU utilization

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Configure AWS CLI
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Build and deploy
        run: |
          sam build
          sam deploy --no-confirm \
            --parameter-overrides \
              DatabaseUrl="postgresql://user:pass@db:5432/mcp" \
            --capabilities CAPABILITY_IAM
```

## 🧪 Testing in AWS

### 1. Health Check

```bash
curl -X GET "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health"
```

### 2. Categories Endpoint

```bash
curl -X POST "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/api/categories" \
  -H "Content-Type: application/json"
```

### 3. Template Rendering

```bash
curl -X POST "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/api/prompts/business_logic/render" \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "business_domain": "e-commerce",
      "requirements": "User authentication system"
    }
  }'
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Issues

```bash
# Check database connectivity
aws rds describe-db-instances --db-instance-identifier your-db-name

# Test connection from Lambda
aws logs tail /aws/lambda/your-function-name --follow
```

#### 2. Lambda Timeout Issues

- Increase memory allocation
- Optimize database queries
- Check Lambda logs in CloudWatch

#### 3. API Gateway Errors

- Check API Gateway configuration
- Verify Lambda function permissions
- Review CloudWatch logs

### Debugging Commands

```bash
# Check Lambda logs
aws logs tail /aws/lambda/your-function-name --follow

# Test Lambda function directly
aws lambda invoke \
  --function-name your-function-name \
  --payload '{"test": "data"}' \
  response.json

# Check API Gateway configuration
aws apigateway get-rest-api --rest-api-id your-api-id
```

## 📈 Performance Optimization

### Lambda Configuration

```yaml
# template.yaml
Resources:
  LambdaFunction:
    Properties:
      MemorySize: 1024  # Increase for better performance
      Timeout: 60       # Increase for complex operations
      ReservedConcurrentExecutions: 20
```

### Database Optimization

- Use connection pooling
- Implement query caching
- Use appropriate indexes
- Monitor slow queries

### API Gateway Optimization

- Enable caching
- Configure throttling
- Use regional endpoints
- Implement WAF protection

## 💰 Cost Optimization

### Cost Components

- **Lambda**: $0.0000002083 per request + $0.0000000021 per GB-second
- **API Gateway**: $3.50 per million API calls
- **RDS PostgreSQL**: $0.034 per GB-month + instance costs
- **CloudWatch**: $0.03 per GB of logs

### Cost-Saving Strategies

1. **Right-size Lambda functions**
2. **Use provisioned concurrency** for predictable workloads
3. **Implement caching** to reduce database calls
4. **Use Reserved Instances** for RDS
5. **Enable data compression** in API Gateway

## 🔄 Scaling Considerations

### Auto-scaling

- Lambda automatically scales based on request volume
- RDS can be configured with read replicas
- API Gateway scales automatically

### High Availability

- Deploy across multiple AZs
- Use RDS Multi-AZ deployment
- Configure API Gateway regional endpoints

## 📋 Deployment Checklist

### Pre-deployment

- [ ] AWS CLI configured
- [ ] SAM CLI installed
- [ ] Docker available
- [ ] Environment variables set
- [ ] Database password generated
- [ ] VPC configured

### Deployment

- [ ] Lambda layer built
- [ ] SAM template validated
- [ ] Dependencies installed
- [ ] Tests passing
- [ ] Database migrations ready

### Post-deployment

- [ ] API endpoints tested
- [ ] Health checks passing
- [ ] Logs accessible
- [ ] Monitoring configured
- [ ] Documentation updated

## 🎯 Next Steps

1. **Set up monitoring** with CloudWatch dashboards
2. **Configure alerting** for error rates and performance
3. **Implement CI/CD** pipeline
4. **Set up domain** with custom domain name
5. **Configure WAF** for security
6. **Implement backup** strategy
7. **Set up staging** environment

## 📚 Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [RDS PostgreSQL Documentation](https://docs.aws.amazon.com/rds/)
- [AWS SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [FastAPI on AWS Lambda](https://mangum.io/)
- [AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/)

---

**🎉 Congratulations! Your MCP-PBA-TUNNEL is now deployed on AWS!**

For support, check the troubleshooting section or create an issue in the repository.
