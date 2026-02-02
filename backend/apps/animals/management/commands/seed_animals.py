"""
Management command to seed animals data.
"""
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from apps.accounts.models import User, Role
from apps.animals.models import (
    Animal, Medication, Vaccination, MedicalProcedure,
    AnimalSpecies, AnimalSex, AnimalStatus
)


class Command(BaseCommand):
    help = 'Seed animals data for demonstration purposes'

    def handle(self, *args, **options):
        self.seed_animals()
        self.seed_medical_records()
        self.stdout.write(self.style.SUCCESS('Animals data seeding completed!'))

    def seed_animals(self):
        animals_data = [
            {
                'animal_id': 'DOG-001',
                'species': AnimalSpecies.DOG,
                'breed': 'Labrador',
                'name': 'Max',
                'birth_date': date(2021, 6, 15),
                'sex': AnimalSex.MALE,
                'coat_color': 'Golden',
                'weight': Decimal('25.50'),
                'status': AnimalStatus.IN_SHELTER,
                'transponder_number': '985120012345678',
            },
            {
                'animal_id': 'CAT-001',
                'species': AnimalSpecies.CAT,
                'breed': 'European Shorthair',
                'name': 'Luna',
                'birth_date': date(2022, 3, 1),
                'sex': AnimalSex.FEMALE,
                'coat_color': 'Black',
                'weight': Decimal('4.20'),
                'status': AnimalStatus.IN_SHELTER,
                'transponder_number': '985120098765432',
            },
            {
                'animal_id': 'DOG-002',
                'species': AnimalSpecies.DOG,
                'breed': 'German Shepherd',
                'name': 'Rocky',
                'birth_date': date(2019, 12, 10),
                'sex': AnimalSex.MALE,
                'coat_color': 'Black and Brown',
                'weight': Decimal('35.00'),
                'status': AnimalStatus.IN_SHELTER,
                'transponder_number': '985120055555555',
            },
            {
                'animal_id': 'CAT-002',
                'species': AnimalSpecies.CAT,
                'breed': 'Mixed',
                'name': 'Mruczek',
                'birth_date': date(2020, 8, 20),
                'sex': AnimalSex.MALE,
                'coat_color': 'Ginger',
                'weight': Decimal('5.50'),
                'status': AnimalStatus.IN_SHELTER,
            },
            {
                'animal_id': 'DOG-003',
                'species': AnimalSpecies.DOG,
                'breed': 'Mixed',
                'name': 'Bella',
                'birth_date': date(2023, 1, 5),
                'sex': AnimalSex.FEMALE,
                'coat_color': 'White with brown patches',
                'weight': Decimal('12.00'),
                'status': AnimalStatus.QUARANTINE,
            },
        ]

        for data in animals_data:
            animal_id = data.pop('animal_id')
            animal, created = Animal.objects.get_or_create(
                animal_id=animal_id,
                defaults=data
            )
            if created:
                self.stdout.write(f'Created animal: {animal.name}')
            else:
                self.stdout.write(self.style.WARNING(f'Animal already exists: {animal.name}'))

    def seed_medical_records(self):
        try:
            vet = User.objects.filter(role=Role.EMPLOYEE).first()
        except User.DoesNotExist:
            vet = None

        # Medications for Max
        try:
            max_dog = Animal.objects.get(animal_id='DOG-001')
            if not max_dog.medications.exists():
                Medication.objects.create(
                    animal=max_dog,
                    medication_name='Amoxicillin',
                    dosage='250mg',
                    frequency='2 times a day',
                    start_date=date.today() - timedelta(days=14),
                    end_date=date.today() - timedelta(days=7),
                    reason='Bacterial infection',
                    notes='Give with food to avoid stomach upset',
                    performed_by=vet,
                )
                self.stdout.write(f'Created medication for Max')
        except Animal.DoesNotExist:
            pass

        # Vaccinations for Max
        try:
            max_dog = Animal.objects.get(animal_id='DOG-001')
            if not max_dog.vaccinations.exists():
                Vaccination.objects.create(
                    animal=max_dog,
                    vaccine_name='Nobivac DHPPi',
                    vaccine_for='Distemper, Parvoviroza, Hepatitis, Parainfluenza',
                    vaccine_batch_number='NV2024A123',
                    vaccination_date=date.today() - timedelta(days=60),
                    expiration_date=date.today() + timedelta(days=305),
                    next_due_date=date.today() + timedelta(days=305),
                    performed_by=vet,
                )
                Vaccination.objects.create(
                    animal=max_dog,
                    vaccine_name='Nobivac Rabies',
                    vaccine_for='Rabies',
                    vaccine_batch_number='NVR2024B456',
                    vaccination_date=date.today() - timedelta(days=30),
                    expiration_date=date.today() + timedelta(days=335),
                    next_due_date=date.today() + timedelta(days=335),
                    performed_by=vet,
                )
                self.stdout.write(f'Created vaccinations for Max')
        except Animal.DoesNotExist:
            pass

        # Procedures for Luna
        try:
            luna = Animal.objects.get(animal_id='CAT-001')
            if not luna.procedures.exists():
                MedicalProcedure.objects.create(
                    animal=luna,
                    procedure_date=date.today() - timedelta(days=90),
                    description='Sterilization',
                    result='Procedure completed successfully, no complications',
                    cost=Decimal('250.00'),
                    notes='Recommended rest for 10 days',
                    performed_by=vet,
                )
                self.stdout.write(f'Created procedure for Luna')
        except Animal.DoesNotExist:
            pass

        # Vaccinations for Luna
        try:
            luna = Animal.objects.get(animal_id='CAT-001')
            if not luna.vaccinations.exists():
                Vaccination.objects.create(
                    animal=luna,
                    vaccine_name='Felocell CVR',
                    vaccine_for='Distemper, Calicivirus, Panleukopenia',
                    vaccine_batch_number='FC2024C789',
                    vaccination_date=date.today() - timedelta(days=45),
                    expiration_date=date.today() + timedelta(days=320),
                    next_due_date=date.today() + timedelta(days=320),
                    performed_by=vet,
                )
                self.stdout.write(f'Created vaccination for Luna')
        except Animal.DoesNotExist:
            pass
