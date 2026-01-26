"""
Tests for animals models.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from apps.animals.models import (
    Animal, Medication, Vaccination, MedicalProcedure,
    AnimalSpecies, AnimalSex, AnimalStatus
)


@pytest.mark.django_db
class TestAnimal:
    """Tests for Animal model."""

    def test_create_animal(self):
        """Test creating an animal."""
        animal = Animal.objects.create(
            animal_id='DOG-001',
            species=AnimalSpecies.DOG,
            breed='Labrador',
            name='Max',
            birth_date=date(2021, 6, 15),
            sex=AnimalSex.MALE,
        )
        assert animal.name == 'Max'
        assert animal.species == AnimalSpecies.DOG
        assert str(animal) == 'Max (Pies)'

    def test_animal_id_unique(self, dog_max):
        """Test that animal_id must be unique."""
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Animal.objects.create(
                animal_id='DOG-001',  # Same as dog_max
                species=AnimalSpecies.DOG,
                name='Rex',
            )

    def test_age_display_years(self):
        """Test age_display for animals older than 1 year."""
        animal = Animal.objects.create(
            animal_id='DOG-002',
            species=AnimalSpecies.DOG,
            name='Rex',
            birth_date=date.today() - timedelta(days=730),  # ~2 years
        )
        assert 'lat' in animal.age_display or 'rok' in animal.age_display

    def test_age_display_months(self):
        """Test age_display for animals less than 1 year old."""
        animal = Animal.objects.create(
            animal_id='DOG-003',
            species=AnimalSpecies.DOG,
            name='Puppy',
            birth_date=date.today() - timedelta(days=90),  # ~3 months
        )
        assert 'mies' in animal.age_display

    def test_age_display_unknown(self):
        """Test age_display when birth_date is not set."""
        animal = Animal.objects.create(
            animal_id='DOG-004',
            species=AnimalSpecies.DOG,
            name='Unknown',
        )
        assert animal.age_display == 'Nieznany'

    def test_default_status(self):
        """Test that default status is NEW_INTAKE."""
        animal = Animal.objects.create(
            animal_id='DOG-005',
            species=AnimalSpecies.DOG,
            name='New Dog',
        )
        assert animal.status == AnimalStatus.NEW_INTAKE


@pytest.mark.django_db
class TestMedication:
    """Tests for Medication model."""

    def test_create_medication(self, dog_max, veterinarian):
        """Test creating a medication record."""
        medication = Medication.objects.create(
            animal=dog_max,
            medication_name='Amoxicylina',
            dosage='250mg',
            frequency='2 razy dziennie',
            start_date=date.today(),
            reason='Infekcja',
            performed_by=veterinarian,
        )
        assert medication.medication_name == 'Amoxicylina'
        assert medication.animal == dog_max
        assert str(medication) == 'Amoxicylina - Max'

    def test_medication_ordering(self, dog_max, veterinarian):
        """Test that medications are ordered by start_date descending."""
        med1 = Medication.objects.create(
            animal=dog_max,
            medication_name='Lek 1',
            dosage='100mg',
            frequency='1 raz dziennie',
            start_date=date.today() - timedelta(days=10),
            reason='Test',
            performed_by=veterinarian,
        )
        med2 = Medication.objects.create(
            animal=dog_max,
            medication_name='Lek 2',
            dosage='200mg',
            frequency='1 raz dziennie',
            start_date=date.today(),
            reason='Test',
            performed_by=veterinarian,
        )
        medications = Medication.objects.filter(animal=dog_max)
        assert medications[0] == med2  # Newer first
        assert medications[1] == med1


@pytest.mark.django_db
class TestVaccination:
    """Tests for Vaccination model."""

    def test_create_vaccination(self, dog_max, veterinarian):
        """Test creating a vaccination record."""
        vaccination = Vaccination.objects.create(
            animal=dog_max,
            vaccine_name='Nobivac DHPPi',
            vaccine_for='Nosówka',
            vaccine_batch_number='AB12345',
            vaccination_date=date.today(),
            expiration_date=date.today() + timedelta(days=365),
            performed_by=veterinarian,
        )
        assert vaccination.vaccine_name == 'Nobivac DHPPi'
        assert str(vaccination) == 'Nobivac DHPPi - Max'


@pytest.mark.django_db
class TestMedicalProcedure:
    """Tests for MedicalProcedure model."""

    def test_create_procedure(self, dog_max, veterinarian):
        """Test creating a medical procedure record."""
        procedure = MedicalProcedure.objects.create(
            animal=dog_max,
            procedure_date=date.today(),
            description='Kastracja',
            result='Pomyślnie',
            cost=Decimal('350.00'),
            performed_by=veterinarian,
        )
        assert procedure.description == 'Kastracja'
        assert procedure.cost == Decimal('350.00')
        assert 'Kastracja' in str(procedure)
