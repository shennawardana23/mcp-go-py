#!/bin/bash
# Deployment script for MCP-PBA-TUNNEL to AWS

set -e

echo "🚀 Deploying MCP-PBA-TUNNEL to AWS..."

# Configuration
STACK_NAME=${STACK_NAME:-"mcp-pba-tunnel"}
REGION=${AWS_REGION:-"us-east-1"}
STAGE=${STAGE:-"prod"}
DB_PASSWORD=${DB_PASSWORD:-"your-secure-password"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  Stack Name: $STACK_NAME"
echo "  Region: $REGION"
echo "  Stage: $STAGE"
echo "  Database Password: [HIDDEN]"

# Validate AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed or not in PATH${NC}"
    echo "Please install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if user is logged in
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not configured${NC}"
    echo "Please configure AWS CLI: aws configure"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI configured${NC}"

# Create deployment package
echo -e "${YELLOW}📦 Building deployment package...${NC}"

# Clean previous builds
rm -f lambda-function.zip

# Install dependencies
pip install -r requirements.txt -t ./build/python/lib/python3.13/site-packages

# Copy source files
mkdir -p build
cp -r server/ build/
cp -r data/ build/
cp -r config/ build/
cp -r mcp/ build/
cp lambda_handler.py build/
cp requirements.txt build/

# Remove unnecessary files
find build -name "*.pyc" -delete
find build -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find build -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find build -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Create deployment package
cd build
zip -r9 ../lambda-function.zip .
cd ..

echo -e "${GREEN}✅ Deployment package created: lambda-function.zip${NC}"
echo -e "${YELLOW}📊 Package size: $(du -sh lambda-function.zip | cut -f1)${NC}"

# Build Lambda Layer
echo -e "${YELLOW}📦 Building Lambda Layer...${NC}"
cd lambda-layer
./build.sh
cd ..

# Validate template
echo -e "${YELLOW}🔍 Validating CloudFormation template...${NC}"
if aws cloudformation validate-template --template-body file://template.yaml --region $REGION; then
    echo -e "${GREEN}✅ Template validation successful${NC}"
else
    echo -e "${RED}❌ Template validation failed${NC}"
    exit 1
fi

# Get user confirmation
echo -e "${YELLOW}⚠️  WARNING: This will deploy resources to AWS${NC}"
echo "  - Lambda Function"
echo "  - API Gateway"
echo "  - RDS PostgreSQL Database"
echo "  - VPC Resources"
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Deploy to AWS
echo -e "${YELLOW}🚀 Deploying to AWS...${NC}"

aws cloudformation deploy \
    --template-file template.yaml \
    --stack-name $STACK_NAME \
    --region $REGION \
    --parameter-overrides \
        StageName=$STAGE \
        DatabaseUrl="postgresql://mcp_user:${DB_PASSWORD}@localhost:5432/mcp_pba_tunnel" \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"

    # Get outputs
    echo -e "${YELLOW}📋 Deployment outputs:${NC}"
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs' \
        --output table

    echo ""
    echo -e "${GREEN}🎉 MCP-PBA-TUNNEL deployed successfully!${NC}"
    echo ""
    echo "📚 Documentation:"
    echo "  - API Endpoint: $(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' --output text)"
    echo "  - Lambda Function: $(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionArn`].OutputValue' --output text)"
    echo "  - Database Endpoint: $(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' --output text)"

else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi
