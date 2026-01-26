param(
    [string]$Environment = "dev"
)

$awsRegion = if ($env:AWS_REGION) { $env:AWS_REGION } else { "us-east-1" }
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$infraRoot = Resolve-Path (Join-Path $scriptDir "..")
$tfDir = Join-Path $infraRoot "terraform"

Write-Host "=== Seeding demo data ==="
Write-Host "Environment: $Environment"
Write-Host "AWS Region: $awsRegion"
Write-Host ""

Set-Location $tfDir

if (-not (Test-Path "terraform.tfstate") -and -not (Test-Path "terraform.tfstate.d\$Environment\terraform.tfstate")) {
    Write-Error "Terraform state not found. Run Terraform before seeding."
    exit 1
}

$ecsCluster = terraform output -raw ecs_cluster_name
$taskDefinition = "shelter-$Environment-backend"
$privateSubnets = terraform output -json private_subnet_ids | ConvertFrom-Json
$subnetList = ($privateSubnets -join ",")

$backendSg = aws ec2 describe-security-groups `
    --filters "Name=tag:Name,Values=shelter-$Environment-backend-sg" `
    --query "SecurityGroups[0].GroupId" `
    --output text `
    --region $awsRegion

if (-not $backendSg -or $backendSg -eq "None") {
    Write-Error "Backend security group not found for environment: $Environment"
    exit 1
}

function Invoke-SeedCommand {
    param([string]$Command)

    Write-Host "Running: python manage.py $Command"
    $overrides = @{
        containerOverrides = @(
            @{ name = "backend"; command = @("python", "manage.py", $Command) }
        )
    } | ConvertTo-Json -Compress

    $networkConfig = "awsvpcConfiguration={subnets=[$subnetList],securityGroups=[$backendSg],assignPublicIp=DISABLED}"

    $taskArn = aws ecs run-task `
        --cluster $ecsCluster `
        --task-definition $taskDefinition `
        --launch-type FARGATE `
        --network-configuration $networkConfig `
        --overrides $overrides `
        --region $awsRegion `
        --query "tasks[0].taskArn" `
        --output text

    Write-Host "Task started: $taskArn"
    aws ecs wait tasks-stopped --cluster $ecsCluster --tasks $taskArn --region $awsRegion | Out-Null

    $exitCode = aws ecs describe-tasks `
        --cluster $ecsCluster `
        --tasks $taskArn `
        --region $awsRegion `
        --query "tasks[0].containers[0].exitCode" `
        --output text

    if ($exitCode -eq "0") {
        Write-Host "$Command completed successfully!"
    } else {
        Write-Error "$Command failed with exit code: $exitCode"
        exit 1
    }

    Write-Host ""
}

Invoke-SeedCommand "seed_oauth_app"
Invoke-SeedCommand "seed_users"
Invoke-SeedCommand "seed_animals"
Invoke-SeedCommand "seed_supplies"

Write-Host "=== Seeding complete! ==="
