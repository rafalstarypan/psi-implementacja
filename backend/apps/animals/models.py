"""
Models for animals app - Animal management and medical records.
"""
from django.db import models
from django.conf import settings
from decimal import Decimal


class AnimalSpecies(models.TextChoices):
    """Animal species."""
    DOG = 'DOG', 'Pies'
    CAT = 'CAT', 'Kot'
    OTHER = 'OTHER', 'Inny'


class AnimalSex(models.TextChoices):
    """Animal sex."""
    MALE = 'MALE', 'Samiec'
    FEMALE = 'FEMALE', 'Samica'
    UNKNOWN = 'UNKNOWN', 'Nieznana'


class AnimalStatus(models.TextChoices):
    """Animal status in the shelter."""
    NEW_INTAKE = 'NEW_INTAKE', 'Nowo przyjęte'
    IN_SHELTER = 'IN_SHELTER', 'W schronisku'
    QUARANTINE = 'QUARANTINE', 'Kwarantanna'
    MEDICAL_TREATMENT = 'MEDICAL_TREATMENT', 'Leczenie'
    ADOPTED = 'ADOPTED', 'Adoptowane'
    DECEASED = 'DECEASED', 'Zmarłe'


class Animal(models.Model):
    """Animal in the shelter."""
    animal_id = models.CharField(
        verbose_name='Identyfikator',
        max_length=50,
        unique=True,
    )
    species = models.CharField(
        verbose_name='Gatunek',
        max_length=10,
        choices=AnimalSpecies.choices,
    )
    breed = models.CharField(
        verbose_name='Rasa',
        max_length=100,
        blank=True,
    )
    name = models.CharField(
        verbose_name='Imię',
        max_length=100,
    )
    birth_date = models.DateField(
        verbose_name='Data urodzenia',
        null=True,
        blank=True,
    )
    sex = models.CharField(
        verbose_name='Płeć',
        max_length=10,
        choices=AnimalSex.choices,
        default=AnimalSex.UNKNOWN,
    )
    coat_color = models.CharField(
        verbose_name='Kolor sierści',
        max_length=100,
        blank=True,
    )
    weight = models.DecimalField(
        verbose_name='Waga (kg)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    identifying_marks = models.TextField(
        verbose_name='Znaki szczególne',
        blank=True,
    )
    transponder_number = models.CharField(
        verbose_name='Numer transpondera (chip)',
        max_length=50,
        blank=True,
        null=True,
        unique=True,
    )
    status = models.CharField(
        verbose_name='Status',
        max_length=20,
        choices=AnimalStatus.choices,
        default=AnimalStatus.NEW_INTAKE,
    )
    notes = models.TextField(
        verbose_name='Uwagi',
        blank=True,
    )
    intake_date = models.DateField(
        verbose_name='Data przyjęcia',
        auto_now_add=True,
    )
    microchipping_date = models.DateField(
        verbose_name='Data chipowania',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Zwierzę'
        verbose_name_plural = 'Zwierzęta'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_species_display()})'

    @property
    def age_display(self):
        """Return age as a human-readable string."""
        if not self.birth_date:
            return 'Nieznany'
        from datetime import date
        today = date.today()
        years = today.year - self.birth_date.year
        months = today.month - self.birth_date.month
        if months < 0:
            years -= 1
            months += 12
        if years > 0:
            return f'{years} lat' if years != 1 else '1 rok'
        return f'{months} mies.' if months > 0 else 'poniżej miesiąca'


class Medication(models.Model):
    """Medication record for an animal."""
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='medications',
        verbose_name='Zwierzę',
    )
    medication_name = models.CharField(
        verbose_name='Nazwa leku',
        max_length=200,
    )
    dosage = models.CharField(
        verbose_name='Dawkowanie',
        max_length=100,
    )
    frequency = models.CharField(
        verbose_name='Częstotliwość podawania',
        max_length=100,
    )
    start_date = models.DateField(
        verbose_name='Data rozpoczęcia',
    )
    end_date = models.DateField(
        verbose_name='Data zakończenia',
        null=True,
        blank=True,
    )
    reason = models.TextField(
        verbose_name='Powód przepisania',
    )
    notes = models.TextField(
        verbose_name='Notatki dodatkowe',
        blank=True,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='prescribed_medications',
        verbose_name='Przepisał',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Przepisany lek'
        verbose_name_plural = 'Przepisane leki'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.medication_name} - {self.animal.name}'


class Vaccination(models.Model):
    """Vaccination record for an animal."""
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='vaccinations',
        verbose_name='Zwierzę',
    )
    vaccine_name = models.CharField(
        verbose_name='Nazwa szczepionki',
        max_length=200,
    )
    vaccine_for = models.CharField(
        verbose_name='Przeciwko (chorobie)',
        max_length=200,
    )
    vaccine_batch_number = models.CharField(
        verbose_name='Numer partii',
        max_length=100,
    )
    vaccination_date = models.DateField(
        verbose_name='Data szczepienia',
    )
    expiration_date = models.DateField(
        verbose_name='Data wygaśnięcia',
    )
    next_due_date = models.DateField(
        verbose_name='Data następnego szczepienia',
        null=True,
        blank=True,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='administered_vaccinations',
        verbose_name='Wykonał',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Szczepienie'
        verbose_name_plural = 'Szczepienia'
        ordering = ['-vaccination_date']

    def __str__(self):
        return f'{self.vaccine_name} - {self.animal.name}'


class MedicalProcedure(models.Model):
    """Medical procedure record for an animal."""
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='procedures',
        verbose_name='Zwierzę',
    )
    procedure_date = models.DateField(
        verbose_name='Data zabiegu',
    )
    description = models.TextField(
        verbose_name='Opis zabiegu',
    )
    result = models.TextField(
        verbose_name='Wynik/Przebieg',
    )
    cost = models.DecimalField(
        verbose_name='Koszt (PLN)',
        max_digits=10,
        decimal_places=2,
    )
    notes = models.TextField(
        verbose_name='Notatki dodatkowe',
        blank=True,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_procedures',
        verbose_name='Wykonał',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Zabieg medyczny'
        verbose_name_plural = 'Zabiegi medyczne'
        ordering = ['-procedure_date']

    def __str__(self):
        return f'{self.description[:50]} - {self.animal.name}'
