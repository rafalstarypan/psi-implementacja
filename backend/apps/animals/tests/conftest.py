"""
Pytest fixtures for animals app tests.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from rest_framework.test import APIClient
from apps.accounts.models import User, Role
from apps.animals.models import (
    Animal, Medication, Vaccination, MedicalProcedure,
    AnimalSpecies, AnimalSex, AnimalStatus
)


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def employee_user(db):
    """Create and return an employee user."""
    return User.objects.create_user(
        email='pracownik@schronisko.pl',
        password='haslo123',
        first_name='Jan',
        last_name='Kowalski',
        role=Role.EMPLOYEE,
    )


@pytest.fixture
def veterinarian(db):
    """Create and return a veterinarian (employee)."""
    return User.objects.create_user(
        email='dr.kowalczyk@schronisko.pl',
        password='haslo123',
        first_name='Maria',
        last_name='Kowalczyk',
        role=Role.EMPLOYEE,
    )


@pytest.fixture
def volunteer_user(db):
    """Create and return a volunteer user."""
    return User.objects.create_user(
        email='wolontariusz@schronisko.pl',
        password='haslo123',
        first_name='Anna',
        last_name='Nowak',
        role=Role.VOLUNTEER,
    )


@pytest.fixture
def authenticated_employee(api_client, employee_user):
    """Return an API client authenticated as an employee."""
    api_client.force_authenticate(user=employee_user)
    return api_client


@pytest.fixture
def authenticated_volunteer(api_client, volunteer_user):
    """Return an API client authenticated as a volunteer."""
    api_client.force_authenticate(user=volunteer_user)
    return api_client


@pytest.fixture
def dog_max(db):
    """Create a dog named Max."""
    return Animal.objects.create(
        animal_id='DOG-001',
        species=AnimalSpecies.DOG,
        breed='Labrador',
        name='Max',
        birth_date=date(2021, 6, 15),
        sex=AnimalSex.MALE,
        coat_color='Złoty',
        weight=Decimal('25.50'),
        status=AnimalStatus.IN_SHELTER,
    )


@pytest.fixture
def cat_luna(db):
    """Create a cat named Luna."""
    return Animal.objects.create(
        animal_id='CAT-001',
        species=AnimalSpecies.CAT,
        breed='Europejski',
        name='Luna',
        birth_date=date(2022, 3, 1),
        sex=AnimalSex.FEMALE,
        coat_color='Czarny',
        weight=Decimal('4.20'),
        status=AnimalStatus.IN_SHELTER,
    )


@pytest.fixture
def animals(dog_max, cat_luna):
    """Return all animals."""
    return [dog_max, cat_luna]


@pytest.fixture
def medication_for_max(db, dog_max, veterinarian):
    """Create a medication record for Max."""
    return Medication.objects.create(
        animal=dog_max,
        medication_name='Amoxicylina',
        dosage='250mg',
        frequency='2 razy dziennie',
        start_date=date.today(),
        end_date=date.today() + timedelta(days=7),
        reason='Infekcja bakteryjna',
        notes='Podawać z jedzeniem',
        performed_by=veterinarian,
    )


@pytest.fixture
def vaccination_for_max(db, dog_max, veterinarian):
    """Create a vaccination record for Max."""
    return Vaccination.objects.create(
        animal=dog_max,
        vaccine_name='Nobivac DHPPi',
        vaccine_for='Nosówka, Parwowiroza',
        vaccine_batch_number='AB12345',
        vaccination_date=date.today(),
        expiration_date=date.today() + timedelta(days=365),
        next_due_date=date.today() + timedelta(days=365),
        performed_by=veterinarian,
    )


@pytest.fixture
def procedure_for_max(db, dog_max, veterinarian):
    """Create a medical procedure record for Max."""
    return MedicalProcedure.objects.create(
        animal=dog_max,
        procedure_date=date.today(),
        description='Kastracja',
        result='Zabieg przebiegł pomyślnie',
        cost=Decimal('350.00'),
        notes='Zalecany odpoczynek przez tydzień',
        performed_by=veterinarian,
    )
