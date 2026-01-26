#!/bin/bash
set -e

# Run database migrations on AWS ECS
# Usage: ./run-migrations.sh [environment]

ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-us-east-1}
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
INFRA_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

echo "=== Running database migrations ==="
echo "Environment: $ENVIRONMENT"
echo ""

cd "$INFRA_ROOT/terraform"

# Get Terraform outputs
ECS_CLUSTER=$(terraform output -raw ecs_cluster_name)
TASK_DEFINITION="shelter-${ENVIRONMENT}-backend"
PRIVATE_SUBNETS=$(terraform output -json private_subnet_ids | jq -r 'join(",")')
BACKEND_SG=$(aws ec2 describe-security-groups \
    --filters "Name=tag:Name,Values=shelter-${ENVIRONMENT}-backend-sg" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region "$AWS_REGION")

echo "Running migration task..."
TASK_ARN=$(aws ecs run-task \
    --cluster "$ECS_CLUSTER" \
    --task-definition "$TASK_DEFINITION" \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[${PRIVATE_SUBNETS}],securityGroups=[${BACKEND_SG}],assignPublicIp=DISABLED}" \
    --overrides '{
        "containerOverrides": [{
            "name": "backend",
            "command": ["python", "manage.py", "migrate"]
        }]
    }' \
    --region "$AWS_REGION" \
    --query 'tasks[0].taskArn' \
    --output text)

echo "Migration task started: $TASK_ARN"
echo "Waiting for task to complete..."

aws ecs wait tasks-stopped \
    --cluster "$ECS_CLUSTER" \
    --tasks "$TASK_ARN" \
    --region "$AWS_REGION"

# Check exit code
EXIT_CODE=$(aws ecs describe-tasks \
    --cluster "$ECS_CLUSTER" \
    --tasks "$TASK_ARN" \
    --region "$AWS_REGION" \
    --query 'tasks[0].containers[0].exitCode' \
    --output text)

if [ "$EXIT_CODE" == "0" ]; then
    echo "Migrations completed successfully!"
else
    echo "Migration failed with exit code: $EXIT_CODE"
    echo "Check CloudWatch logs for details."
    exit 1
fi
