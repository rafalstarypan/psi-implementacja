#!/bin/bash
set -e

# Build and push Docker images to ECR
# Usage: ./build-and-push.sh [environment]

ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-us-east-1}
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
INFRA_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
PROJECT_ROOT=$(cd "$INFRA_ROOT/.." && pwd)

echo "=== Building and pushing Docker images ==="
echo "Environment: $ENVIRONMENT"
echo "AWS Region: $AWS_REGION"
echo ""

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Get repository URLs from Terraform output
cd "$INFRA_ROOT/terraform"
BACKEND_REPO=$(terraform output -raw ecr_backend_repository_url 2>/dev/null || true)
FRONTEND_REPO=$(terraform output -raw ecr_frontend_repository_url 2>/dev/null || true)

if [ -z "$BACKEND_REPO" ]; then
    BACKEND_REPO="${ECR_REGISTRY}/shelter-${ENVIRONMENT}-backend"
fi

if [ -z "$FRONTEND_REPO" ]; then
    FRONTEND_REPO="${ECR_REGISTRY}/shelter-${ENVIRONMENT}-frontend"
fi

GIT_SHA=""
if git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git rev-parse --verify HEAD >/dev/null 2>&1; then
    GIT_SHA=$(git rev-parse --short HEAD)
fi

if [ -z "$GIT_SHA" ]; then
    GIT_SHA=$(date +%Y%m%d%H%M%S)
fi

# Build and push backend
echo ""
echo "=== Building backend image ==="
cd "$PROJECT_ROOT/backend"
docker build -t shelter-backend:latest .
docker tag shelter-backend:latest "${BACKEND_REPO}:latest"
docker tag shelter-backend:latest "${BACKEND_REPO}:${GIT_SHA}"

echo "Pushing backend image..."
docker push "${BACKEND_REPO}:latest"
docker push "${BACKEND_REPO}:${GIT_SHA}"

# Build and push frontend
echo ""
echo "=== Building frontend image ==="
cd "$PROJECT_ROOT/frontend"

# Get ALB DNS from Terraform for API URL
ALB_DNS=$(cd "$INFRA_ROOT/terraform" && terraform output -raw alb_dns_name 2>/dev/null || echo "localhost")

docker build \
    --build-arg VITE_API_URL="http://${ALB_DNS}/api" \
    --build-arg VITE_OAUTH_CLIENT_ID="shelter-frontend" \
    -t shelter-frontend:latest .

docker tag shelter-frontend:latest "${FRONTEND_REPO}:latest"
docker tag shelter-frontend:latest "${FRONTEND_REPO}:${GIT_SHA}"

echo "Pushing frontend image..."
docker push "${FRONTEND_REPO}:latest"
docker push "${FRONTEND_REPO}:${GIT_SHA}"

echo ""
echo "=== Done! ==="
echo "Backend image: ${BACKEND_REPO}:latest"
echo "Frontend image: ${FRONTEND_REPO}:latest"
