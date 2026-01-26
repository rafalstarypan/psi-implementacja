#!/bin/bash
set -e

# Seed demo data on AWS ECS
# Usage: ./seed-data.sh [environment]

ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-us-east-1}
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
INFRA_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

echo "=== Seeding demo data ==="
echo "Environment: $ENVIRONMENT"
echo ""

cd "$INFRA_ROOT/terraform"

# Get Terraform outputs
ECS_CLUSTER=$(terraform output -raw ecs_cluster_name)
TASK_DEFINITION="shelter-${ENVIRONMENT}-backend"
PRIVATE_SUBNETS=$(terraform output -json private_subnet_ids | tr -d '[]"' | tr ',' ',')
BACKEND_SG=$(aws ec2 describe-security-groups \
    --filters "Name=tag:Name,Values=shelter-${ENVIRONMENT}-backend-sg" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region "$AWS_REGION")

run_seed_command() {
    local command=$1
    echo "Running: python manage.py $command"

    TASK_ARN=$(aws ecs run-task \
        --cluster "$ECS_CLUSTER" \
        --task-definition "$TASK_DEFINITION" \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[${PRIVATE_SUBNETS}],securityGroups=[${BACKEND_SG}],assignPublicIp=DISABLED}" \
        --overrides "{
            \"containerOverrides\": [{
                \"name\": \"backend\",
                \"command\": [\"python\", \"manage.py\", \"$command\"]
            }]
        }" \
        --region "$AWS_REGION" \
        --query 'tasks[0].taskArn' \
        --output text)

    echo "Task started: $TASK_ARN"

    aws ecs wait tasks-stopped \
        --cluster "$ECS_CLUSTER" \
        --tasks "$TASK_ARN" \
        --region "$AWS_REGION"

    EXIT_CODE=$(aws ecs describe-tasks \
        --cluster "$ECS_CLUSTER" \
        --tasks "$TASK_ARN" \
        --region "$AWS_REGION" \
        --query 'tasks[0].containers[0].exitCode' \
        --output text)

    if [ "$EXIT_CODE" == "0" ]; then
        echo "$command completed successfully!"
    else
        echo "$command failed with exit code: $EXIT_CODE"
    fi
    echo ""
}

# Seed users
run_seed_command "seed_oauth_app"
run_seed_command "seed_users"

# Seed animals
run_seed_command "seed_animals"

# Seed supplies
run_seed_command "seed_supplies"

echo "=== Seeding complete! ==="
echo ""
echo "Demo accounts (password: haslo123):"
echo "  - pracownik@schronisko.pl (Pracownik)"
echo "  - wolontariusz@schronisko.pl (Wolontariusz)"
echo "  - odwiedzajacy@schronisko.pl (Odwiedzający)"
