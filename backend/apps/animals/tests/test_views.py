"""
Tests for animals views.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.urls import reverse
from apps.animals.models import AnimalSpecies


@pytest.mark.django_db
class TestAnimalViewSet:
    """Tests for AnimalViewSet."""

    def test_list_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access the endpoint."""
        url = reverse('animals:animal-list')
        response = api_client.get(url)
        assert response.status_code == 401

    def test_list_requires_employee_role(self, authenticated_volunteer):
        """Test that volunteers cannot access animals."""
        url = reverse('animals:animal-list')
        response = authenticated_volunteer.get(url)
        assert response.status_code == 403

    def test_list_returns_animals_for_employee(self, authenticated_employee, animals):
        """Test that employees can list animals."""
        url = reverse('animals:animal-list')
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert len(response.data['results']) == len(animals)

    def test_list_search_by_name(self, authenticated_employee, animals):
        """Test searching animals by name."""
        url = reverse('animals:animal-list')
        response = authenticated_employee.get(url, {'search': 'max'})

        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Max'

    def test_list_filter_by_species(self, authenticated_employee, animals):
        """Test filtering animals by species."""
        url = reverse('animals:animal-list')
        response = authenticated_employee.get(url, {'species': AnimalSpecies.DOG})

        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['species'] == AnimalSpecies.DOG

    def test_retrieve_animal_details(self, authenticated_employee, dog_max):
        """Test retrieving a single animal."""
        url = reverse('animals:animal-detail', kwargs={'pk': dog_max.id})
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert response.data['id'] == dog_max.id
        assert response.data['name'] == dog_max.name
        assert response.data['species'] == AnimalSpecies.DOG
        assert response.data['species_display'] == 'Dog'


@pytest.mark.django_db
class TestMedicationEndpoints:
    """Tests for medication endpoints."""

    def test_list_medications(self, authenticated_employee, dog_max, medication_for_max):
        """Test listing medications for an animal."""
        url = reverse('animals:animal-medications', kwargs={'pk': dog_max.id})
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['medication_name'] == 'Amoxicylina'

    def test_create_medication(self, authenticated_employee, dog_max, veterinarian):
        """Test creating a medication record."""
        url = reverse('animals:animal-medications', kwargs={'pk': dog_max.id})
        data = {
            'medication_name': 'Ibuprofen',
            'dosage': '100mg',
            'frequency': '3 razy dziennie',
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=5)),
            'reason': 'Ból',
            'performed_by': veterinarian.id,
        }
        response = authenticated_employee.post(url, data)

        assert response.status_code == 201
        assert response.data['medication_name'] == 'Ibuprofen'

    def test_create_medication_without_performed_by(self, authenticated_employee, dog_max):
        """Test that performed_by defaults to current user."""
        url = reverse('animals:animal-medications', kwargs={'pk': dog_max.id})
        data = {
            'medication_name': 'Paracetamol',
            'dosage': '500mg',
            'frequency': '2 razy dziennie',
            'start_date': str(date.today()),
            'reason': 'Gorączka',
        }
        response = authenticated_employee.post(url, data)

        assert response.status_code == 201
        assert response.data['performed_by'] is not None


@pytest.mark.django_db
class TestVaccinationEndpoints:
    """Tests for vaccination endpoints."""

    def test_list_vaccinations(self, authenticated_employee, dog_max, vaccination_for_max):
        """Test listing vaccinations for an animal."""
        url = reverse('animals:animal-vaccinations', kwargs={'pk': dog_max.id})
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['vaccine_name'] == 'Nobivac DHPPi'

    def test_create_vaccination(self, authenticated_employee, dog_max, veterinarian):
        """Test creating a vaccination record."""
        url = reverse('animals:animal-vaccinations', kwargs={'pk': dog_max.id})
        data = {
            'vaccine_name': 'Rabies',
            'vaccine_for': 'Wścieklizna',
            'vaccine_batch_number': 'XY98765',
            'vaccination_date': str(date.today()),
            'expiration_date': str(date.today() + timedelta(days=365)),
            'performed_by': veterinarian.id,
        }
        response = authenticated_employee.post(url, data)

        assert response.status_code == 201
        assert response.data['vaccine_name'] == 'Rabies'


@pytest.mark.django_db
class TestMedicalProcedureEndpoints:
    """Tests for medical procedure endpoints."""

    def test_list_procedures(self, authenticated_employee, dog_max, procedure_for_max):
        """Test listing procedures for an animal."""
        url = reverse('animals:animal-procedures', kwargs={'pk': dog_max.id})
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['description'] == 'Kastracja'

    def test_create_procedure(self, authenticated_employee, dog_max, veterinarian):
        """Test creating a medical procedure record."""
        url = reverse('animals:animal-procedures', kwargs={'pk': dog_max.id})
        data = {
            'procedure_date': str(date.today()),
            'description': 'Czyszczenie zębów',
            'result': 'Pomyślnie',
            'cost': '150.00',
            'performed_by': veterinarian.id,
        }
        response = authenticated_employee.post(url, data)

        assert response.status_code == 201
        assert response.data['description'] == 'Czyszczenie zębów'
        assert Decimal(response.data['cost']) == Decimal('150.00')


@pytest.mark.django_db
class TestVeterinarianListView:
    """Tests for VeterinarianListView."""

    def test_list_veterinarians(self, authenticated_employee, employee_user, veterinarian):
        """Test listing veterinarians."""
        url = reverse('animals:veterinarian-list')
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert len(response.data) >= 2  # At least employee_user and veterinarian

    def test_list_requires_employee(self, authenticated_volunteer):
        """Test that volunteers cannot access veterinarians list."""
        url = reverse('animals:veterinarian-list')
        response = authenticated_volunteer.get(url)
        assert response.status_code == 403
