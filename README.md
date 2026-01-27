# System Zarządzania Schroniskiem dla Zwierząt

Aplikacja webowa do zarządzania schroniskiem dla zwierząt, zaimplementowana w ramach przedmiotu Projektowanie Systemów Informatycznych.

## Funkcjonalności

### Moduł Autentykacji

- Logowanie użytkowników z trzema rolami:
  - **Pracownik** - pełny dostęp do wszystkich funkcji
  - **Wolontariusz** - dostęp do odczytu i modyfikacji danych
  - **Odwiedzający** - dostęp tylko do odczytu
- Autoryzacja OAuth2 (Resource Owner Password Grant)

### Moduł Zaopatrzenia

- Przeglądanie listy produktów z filtrowaniem
- Szczegóły produktu z historią operacji
- Przyjęcie towaru (PZ) - tylko Pracownik/Wolontariusz
- Wydanie towaru (WZ) - tylko Pracownik/Wolontariusz
- Monitorowanie stanów magazynowych (Dobry/Uwaga/Niski)

### Moduł Historii Zdrowia Zwierząt

- Lista zwierząt z filtrowaniem po gatunku i statusie
- Karta zdrowia zwierzęcia z zakładkami:
  - Leki (dodawanie, przeglądanie historii)
  - Szczepienia (rejestracja, przypomnienia)
  - Zabiegi medyczne (dokumentacja procedur)
- Dodawanie wpisów medycznych - tylko Pracownik

## Technologie

### Backend

- Python 3.11
- Django 5.x
- Django REST Framework
- django-oauth-toolkit
- PostgreSQL
- pytest (testy jednostkowe i integracyjne)

### Frontend

- React 18
- TypeScript
- Vite
- TailwindCSS
- shadcn/ui
- TanStack Query
- React Router

### Infrastruktura

- Docker & Docker Compose
- Terraform
- AWS (ECS Fargate, RDS, ALB, ECR)

## Uruchomienie lokalne

### Wymagania

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Szybki start (Windows)

```batch
cd infrastructure\scripts
setup-local.bat
```

### Szybki start (Linux/Mac)

```bash
chmod +x infrastructure/scripts/*.sh
./infrastructure/scripts/setup-local.sh
```

### Uruchomienie ręczne

1. **Uruchom bazę danych PostgreSQL**

   ```bash
   docker-compose up -d
   ```

2. **Skonfiguruj backend**

   ```bash
   cd backend
   python -m venv venv

   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate

   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_users
   python manage.py seed_animals
   python manage.py seed_supplies
   python manage.py runserver
   ```

3. **Skonfiguruj frontend**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Otwórz aplikację**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/api
   - Admin: http://localhost:8000/admin

### Django Admin

- Superuser (tworzony przez `seed_users`):
  - Email: `admin@schronisko.pl`
  - Haslo: `admin123`
- URL lokalnie: `http://localhost:8000/admin/`
- URL na AWS: `http://<ALB_Z_TERRAFORM>/admin/`
  - Uzyj ALB z: `cd infrastructure/terraform && terraform output -raw alb_dns_name`
### Konta demonstracyjne

| Email                      | Hasło    | Rola         |
| -------------------------- | -------- | ------------ |
| pracownik@schronisko.pl    | haslo123 | Pracownik    |
| wolontariusz@schronisko.pl | haslo123 | Wolontariusz |
| odwiedzajacy@schronisko.pl | haslo123 | Odwiedzający |

## Wdrozenie na AWS

### Cel procedury

Procedura ponizej zapewnia spojnosci miedzy:

- ALB utworzonym przez Terraform,
- adresem API w frontendzie,
- oraz seedingiem danych w tej samej infrastrukturze.

Najwazniejsze zalozenie: zawsze korzystamy z ALB zwracanego przez `terraform output -raw alb_dns_name`.

### Wymagania

- AWS CLI skonfigurowane z odpowiednimi uprawnieniami
- Terraform 1.0+
- Docker

### Procedura krok po kroku (DEV)

1. Skonfiguruj zmienne Terraform

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Edytuj terraform.tfvars i ustaw wymagane wartosci
# Learner Lab: ustaw aws_region=us-east-1 i availability_zones na dwa AZ
```

2. Zbuduj / zaktualizuj infrastrukture

```bash
cd infrastructure/terraform
terraform init
terraform apply -var="environment=dev"
```

3. Pobierz i zapisz wlasciwy ALB DNS (punkt odniesienia)

```bash
cd infrastructure/terraform
terraform output -raw alb_dns_name
```

To jest jedyny poprawny adres ALB dla danego stanu Terraform.

4. Zbuduj i wypchnij obrazy z ALB z Terraform output

```bash
cd infrastructure/scripts
chmod +x *.sh
./build-and-push.sh dev
```

Ten skrypt:

- pobiera ALB DNS z `terraform output -raw alb_dns_name`,
- ustawia go jako `VITE_API_URL=http://<ALB>/api` podczas buildu frontendu,
- a nastepnie pushuje obrazy do ECR.

5. Wymus nowy deploy uslug ECS

```bash
aws ecs update-service --cluster shelter-dev-cluster --service shelter-dev-backend-service --force-new-deployment --region us-east-1
aws ecs update-service --cluster shelter-dev-cluster --service shelter-dev-frontend-service --force-new-deployment --region us-east-1
```

Migracje uruchamiaja sie automatycznie przy starcie backendu.

6. Uruchom seedy na AWS (nie lokalnie)

Linux/Mac:

```bash
cd infrastructure/scripts
./seed-data.sh dev
```

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File infrastructure/scripts/seed-data.ps1 dev
```

7. Testuj wylacznie na ALB z kroku 3

Sprawdz w przegladarce:

- Admin: `http://<ALB_Z_TERRAFORM>/admin/`
- Statyki admina: `http://<ALB_Z_TERRAFORM>/static/admin/css/base.css`
- Token: `http://<ALB_Z_TERRAFORM>/o/token/`

### Dlaczego ta procedura rozwiazuje problemy

- `/admin` i jego statyki dzialaja poprawnie, bo ALB routuje `/admin/*` i `/static/*` do backendu.
- Logowanie dziala, bo:
  - frontend jest budowany z poprawnym ALB DNS,
  - a seedy odpalane sa na tej samej infrastrukturze (ECS + RDS) co ALB z Terraform output.

Najczestsza przyczyna bledow: korzystanie z innego ALB niz ten wynikajacy z biezacego stanu Terraform.

## Testowanie

### Testy backend

```bash
cd backend
source venv/bin/activate  # lub venv\Scripts\activate na Windows
pytest
pytest --cov=apps         # z pokryciem kodu
pytest --cov=apps --cov-report=html  # raport HTML w htmlcov/
```

### Struktura testów

```
backend/apps/
├── accounts/tests/
│   ├── conftest.py           # Fixtures
│   ├── test_models.py        # Testy modeli
│   ├── test_views.py         # Testy widoków API
│   └── test_permissions.py   # Testy uprawnień
│
├── animals/tests/
│   ├── conftest.py
│   ├── test_models.py
│   └── test_views.py
│
└── supplies/tests/
    ├── conftest.py
    ├── test_models.py
    ├── test_views.py
    └── test_filters.py
```

## API Endpoints

### Autentykacja

- `POST /o/token/` - Uzyskanie tokena OAuth2
- `GET /api/auth/me/` - Dane zalogowanego użytkownika

### Zaopatrzenie

- `GET /api/supplies/items/` - Lista produktów
- `GET /api/supplies/items/{id}/` - Szczegóły produktu
- `POST /api/supplies/items/{id}/update_inventory/` - Aktualizacja stanu
- `GET /api/supplies/categories/` - Lista kategorii

### Zwierzęta

- `GET /api/animals/` - Lista zwierząt
- `GET /api/animals/{id}/` - Szczegóły zwierzęcia
- `GET /api/animals/{id}/medications/` - Lista leków
- `POST /api/animals/{id}/medications/` - Dodaj lek
- `GET /api/animals/{id}/vaccinations/` - Lista szczepień
- `POST /api/animals/{id}/vaccinations/` - Dodaj szczepienie
- `GET /api/animals/{id}/procedures/` - Lista zabiegów
- `POST /api/animals/{id}/procedures/` - Dodaj zabieg

## Przydatne komendu do deploymentu

- aws sts get-caller-identity
- docker system prune -a --volumes -f

