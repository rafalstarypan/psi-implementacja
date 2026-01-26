@echo off
setlocal enabledelayedexpansion

REM Setup local development environment for Windows
REM Usage: setup-local.bat

set SCRIPT_DIR=%~dp0
set INFRA_ROOT=%SCRIPT_DIR%..
set PROJECT_ROOT=%INFRA_ROOT%\..

echo === Setting up local development environment ===
echo.

REM Step 1: Start PostgreSQL with Docker Compose
echo === Step 1: Starting PostgreSQL ===
cd /d "%PROJECT_ROOT%"
docker-compose up -d

echo Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak > nul

:wait_postgres
docker-compose exec -T db pg_isready -U shelter_user -d shelter_db > nul 2>&1
if errorlevel 1 (
    echo Waiting for PostgreSQL...
    timeout /t 2 /nobreak > nul
    goto wait_postgres
)
echo PostgreSQL is ready!

REM Step 2: Setup Backend
echo.
echo === Step 2: Setting up Backend ===
cd /d "%PROJECT_ROOT%\backend"

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    (
        echo DEBUG=True
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo DATABASE_URL=postgres://shelter_user:shelter_password@localhost:5432/shelter_db
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo CORS_ALLOWED_ORIGINS=http://localhost:5173
    ) > .env
)

REM Create migrations directories if they don't exist
if not exist "apps\accounts\migrations" (
    mkdir apps\accounts\migrations
    type nul > apps\accounts\migrations\__init__.py
)
if not exist "apps\animals\migrations" (
    mkdir apps\animals\migrations
    type nul > apps\animals\migrations\__init__.py
)
if not exist "apps\supplies\migrations" (
    mkdir apps\supplies\migrations
    type nul > apps\supplies\migrations\__init__.py
)
if not exist "apps\core\migrations" (
    mkdir apps\core\migrations
    type nul > apps\core\migrations\__init__.py
)

REM Create migrations (accounts FIRST because admin depends on custom User model)
echo Creating database migrations...
python manage.py makemigrations accounts
python manage.py makemigrations animals supplies core

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Create OAuth2 application
echo Creating OAuth2 application...
python manage.py shell -c "from oauth2_provider.models import Application; Application.objects.get_or_create(client_id='shelter-frontend', defaults={'name': 'Shelter Frontend', 'client_type': 'public', 'authorization_grant_type': 'password', 'skip_authorization': True})"

REM Seed demo data
echo Seeding demo data...
python manage.py seed_users
python manage.py seed_animals 2>nul || echo seed_animals command not found or failed
python manage.py seed_supplies 2>nul || echo seed_supplies command not found or failed

echo.
echo Backend setup complete!

REM Step 3: Setup Frontend
echo.
echo === Step 3: Setting up Frontend ===
cd /d "%PROJECT_ROOT%\frontend"

echo Installing Node.js dependencies...
call npm install

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    (
        echo VITE_API_URL=http://localhost:8000/api
        echo VITE_OAUTH_CLIENT_ID=shelter-frontend
    ) > .env
)

echo.
echo Frontend setup complete!

echo.
echo === Setup Complete! ===
echo.
echo To start the application:
echo   1. Backend:  cd backend ^& venv\Scripts\activate ^& python manage.py runserver
echo   2. Frontend: cd frontend ^& npm run dev
echo.
echo Demo accounts:
echo   - admin@schronisko.pl / admin123 (Admin - Django Admin access)
echo   - pracownik@schronisko.pl / haslo123 (Pracownik)
echo   - wolontariusz@schronisko.pl / haslo123 (Wolontariusz)
echo   - odwiedzajacy@schronisko.pl / haslo123 (Odwiedzajacy)
echo.
echo Django Admin: http://localhost:8000/admin/
echo.

pause
