"""
Tests for animals models.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from apps.animals.models import (
    Animal, Medication, Vaccination, MedicalProcedure,
    AnimalSpecies, AnimalSex, AnimalStatus, BehavioralTag, Intake,
    IntakeType, AnimalSpecies
)
from django.core.exceptions import ValidationError


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
        assert str(animal) == 'Max (Dog)'

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
        assert 'years' in animal.age_display or 'year' in animal.age_display

    def test_age_display_months(self):
        """Test age_display for animals less than 1 year old."""
        animal = Animal.objects.create(
            animal_id='DOG-003',
            species=AnimalSpecies.DOG,
            name='Puppy',
            birth_date=date.today() - timedelta(days=90),  # ~3 months
        )
        assert 'months' in animal.age_display

    def test_age_display_unknown(self):
        """Test age_display when birth_date is not set."""
        animal = Animal.objects.create(
            animal_id='DOG-004',
            species=AnimalSpecies.DOG,
            name='Unknown',
        )
        assert animal.age_display == 'Unknown'

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


@pytest.mark.django_db
class TestBehavioralTag:
    """Tests for BehavioralTag model."""

    def test_create_tag(self):
        """Test creating a behavioral tag."""
        tag = BehavioralTag.objects.create(
            behavioral_tag_name='Agresywny',
            description='Wykazuje agresję przy jedzeniu'
        )
        assert tag.behavioral_tag_name == 'Agresywny'
        assert str(tag) == 'Agresywny'

    def test_tag_name_unique(self):
        """Test that behavioral_tag_name must be unique."""
        BehavioralTag.objects.create(
            behavioral_tag_name='Lękliwy',
            description='Boi się hałasu'
        )
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            BehavioralTag.objects.create(
                behavioral_tag_name='Lękliwy',
                description='Inny opis'
            )


@pytest.mark.django_db
class TestAnimalExtended:
    """Additional tests for Animal model features not covered in original tests."""

    def test_age_display_less_than_month(self):
        """Test age_display for animals born recently."""
        animal = Animal.objects.create(
            name='Baby',
            species=AnimalSpecies.CAT,
            birth_date=date.today() - timedelta(days=10)
        )
        assert animal.age_display == '1 months.'

    def test_parent_validation_limit(self):
        """Test that an animal cannot have more than 2 parents."""
        child = Animal.objects.create(name='Child', species=AnimalSpecies.DOG)
        parent1 = Animal.objects.create(name='Parent1', species=AnimalSpecies.DOG)
        parent2 = Animal.objects.create(name='Parent2', species=AnimalSpecies.DOG)
        parent3 = Animal.objects.create(name='Parent3', species=AnimalSpecies.DOG)


        child.parents.add(parent1, parent2, parent3)


        with pytest.raises(ValidationError) as excinfo:
            child.clean()
        
        assert "An animal can have at most 2 parents" in str(excinfo.value)

    def test_add_behavioral_tags(self):
        """Test associating behavioral tags with an animal."""
        animal = Animal.objects.create(name='Burek', species=AnimalSpecies.DOG)
        tag = BehavioralTag.objects.create(
            behavioral_tag_name='Przyjazny', 
            description='Lubi ludzi'
        )
        
        animal.behavioral_tags.add(tag)
        assert animal.behavioral_tags.count() == 1
        assert animal.behavioral_tags.first() == tag


@pytest.mark.django_db
class TestIntake:
    """Tests for Intake model."""

    def test_create_intake(self, dog_max):
        """Test creating an intake record."""
        intake = Intake.objects.create(
            animal=dog_max,
            intake_date=date.today(),
            animal_condition='Dobry',
            location='Ul. Główna 5',
            notes='Znaleziony przy sklepie',
            intake_type=IntakeType.STRAY,
            source_type='person'
        )
        
        assert intake.animal == dog_max
        assert intake.intake_type == IntakeType.STRAY

        expected_str = f'{dog_max.name} - {date.today()} - {IntakeType.STRAY.label}'
        assert str(intake) == expected_str

    def test_intake_defaults(self, dog_max):
        """Test default values for intake."""
        intake = Intake.objects.create(
            animal=dog_max,
            animal_condition='Zły',
            location='Las',
            notes='Brak',
            intake_type=IntakeType.SURRENDER
        )
        assert intake.intake_date == date.today()
        assert intake.intake_id is not None


