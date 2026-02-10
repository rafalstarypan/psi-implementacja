#!/bin/bash
set -e

# Setup local development environment
# Usage: ./setup-local.sh

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
INFRA_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
PROJECT_ROOT=$(cd "$INFRA_ROOT/.." && pwd)

echo "=== Setting up local development environment ==="
echo ""

# Step 1: Start PostgreSQL with Docker Compose
echo "=== Step 1: Starting PostgreSQL ==="
cd "$PROJECT_ROOT"
docker-compose up -d

echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Check if PostgreSQL is ready
until docker-compose exec -T db pg_isready -U shelter_user -d shelter_db; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo "PostgreSQL is ready!"

# Step 2: Setup Backend
echo ""
echo "=== Step 2: Setting up Backend ==="
cd "$PROJECT_ROOT/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgres://shelter_user:shelter_password@localhost:5432/shelter_db
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
EOF
fi

# Create migrations directories if they don't exist
for app in accounts animals supplies core; do
    if [ ! -d "apps/$app/migrations" ]; then
        mkdir -p "apps/$app/migrations"
        touch "apps/$app/migrations/__init__.py"
    fi
done

# Create migrations (accounts FIRST because admin depends on custom User model)
echo "Creating database migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations animals supplies core

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create OAuth2 application
echo "Creating OAuth2 application..."
python manage.py shell << 'PYTHON_EOF'
from oauth2_provider.models import Application
from django.contrib.auth import get_user_model

User = get_user_model()

# Create or get application
app, created = Application.objects.get_or_create(
    client_id='shelter-frontend',
    defaults={
        'name': 'Shelter Frontend',
        'client_type': Application.CLIENT_PUBLIC,
        'authorization_grant_type': Application.GRANT_PASSWORD,
        'skip_authorization': True,
    }
)
if created:
    print("OAuth2 application created: shelter-frontend")
else:
    print("OAuth2 application already exists: shelter-frontend")
PYTHON_EOF

# Seed demo data
echo "Seeding demo data..."
python manage.py seed_users
python manage.py seed_animals || echo "seed_animals command not found or failed"
python manage.py seed_supplies || echo "seed_supplies command not found or failed"
python manage.py seed_behavioral_tags || echo seed_behavioral_tags command not found or failed
python manage.py seed_tasks || echo seed_tasks command not found or failed


echo ""
echo "Backend setup complete!"
echo "Run 'cd backend && source venv/bin/activate && python manage.py runserver' to start the backend"

# Step 3: Setup Frontend
echo ""
echo "=== Step 3: Setting up Frontend ==="
cd "$PROJECT_ROOT/frontend"

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
VITE_API_URL=http://localhost:8000/api
VITE_OAUTH_CLIENT_ID=shelter-frontend
EOF
fi

echo ""
echo "Frontend setup complete!"
echo "Run 'cd frontend && npm run dev' to start the frontend"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To start the application:"
echo "  1. Backend:  cd backend && source venv/bin/activate && python manage.py runserver"
echo "  2. Frontend: cd frontend && npm run dev"
echo ""
echo "Demo accounts:"
echo "  - admin@schronisko.pl / admin123 (Admin - Django Admin access)"
echo "  - pracownik@schronisko.pl / haslo123 (Pracownik)"
echo "  - wolontariusz@schronisko.pl / haslo123 (Wolontariusz)"
echo "  - odwiedzajacy@schronisko.pl / haslo123 (Odwiedzający)"
echo ""
echo "Django Admin: http://localhost:8000/admin/"
