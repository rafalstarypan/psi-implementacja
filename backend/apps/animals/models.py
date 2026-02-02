"""
Models for animals app - Animal management and medical records.
"""
from datetime import date
from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid
from django.core.exceptions import ValidationError


class AnimalSpecies(models.TextChoices):
    """Animal species."""
    DOG = 'DOG', 'Dog'
    CAT = 'CAT', 'Cat'
    OTHER = 'OTHER', 'Other'


class AnimalSex(models.TextChoices):
    """Animal sex."""
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    UNKNOWN = 'UNKNOWN', 'Unknown'


class AnimalStatus(models.TextChoices):
    """Animal status in the shelter."""
    NEW_INTAKE = 'NEW_INTAKE', 'Newly Intake'
    IN_SHELTER = 'IN_SHELTER', 'In Shelter'
    QUARANTINE = 'QUARANTINE', 'Quarantine'
    MEDICAL_TREATMENT = 'MEDICAL_TREATMENT', 'Medical Treatment'
    ADOPTED = 'ADOPTED', 'Adopted'
    DECEASED = 'DECEASED', 'Deceased'


class IntakeType(models.TextChoices):
    """Type of animal intake."""
    STRAY = 'STRAY', 'Stray'
    SURRENDER = 'SURRENDER', 'Surrender'
    CONFISCATION = 'CONFISCATION', 'Confiscation'
    TRANSFER = 'TRANSFER', 'Transfer'
    BORN_IN_SHELTER = 'BORN_IN_SHELTER', 'Born in Shelter'



class BehavioralTag(models.Model):
    """Behavioral tag for animals."""
    behavioral_tag_name = models.CharField(
        verbose_name='Behavioral Tag Name',
        max_length=50,
        unique=True,  
        editable=False,
    )
    description = models.CharField(
        verbose_name='Description',
        max_length=255,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Behavioral Tag'
        verbose_name_plural = 'Behavioral Tags'
        ordering = ['-behavioral_tag_name']
    def __str__(self):
        return self.behavioral_tag_name

class Animal(models.Model):
    """Animal in the shelter."""
    animal_id = models.CharField(
        verbose_name='Identifier',
        max_length=50,
        unique=True,
        default=uuid.uuid4,  
        editable=False,
    )
    species = models.CharField(
        verbose_name='Species',
        max_length=10,
        choices=AnimalSpecies.choices,
    )
    breed = models.CharField(
        verbose_name='Breed',
        max_length=100,
        blank=True,
    )
    name = models.CharField(
        verbose_name='Name',
        max_length=100,
    )
    birth_date = models.DateField(
        verbose_name='Birth Date',
        null=True,
        blank=True,
    )
    sex = models.CharField(
        verbose_name='Sex',
        max_length=10,
        choices=AnimalSex.choices,
        default=AnimalSex.UNKNOWN,
    )
    coat_color = models.CharField(
        verbose_name='Coat Color',
        max_length=100,
        blank=True,
    )
    weight = models.DecimalField(
        verbose_name='Weight (kg)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    identifying_marks = models.TextField(
        verbose_name='Identifying Marks',
        blank=True,
    )
    transponder_number = models.CharField(
        verbose_name='Transponder Number(microchip)',
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
        verbose_name='Notes',
        blank=True,
    )
    intake_date = models.DateField(
        verbose_name='Intake Date',
        auto_now_add=True,
    )
    microchipping_date = models.DateField(
        verbose_name='Microchipping Date',
        null=True,
        blank=True,
    )

    last_measured = models.DateField(
        verbose_name='Last measured date',
        null=True,
        blank=True,
    )

    behavioral_tags = models.ManyToManyField(
        BehavioralTag,
        related_name="animals",
        blank=True,
    )

    parents = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='offspring',
        blank=True,
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Animal'
        verbose_name_plural = 'Animals'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_species_display()})'
    
    def clean(self):
        super().clean()
        if self.pk and self.parents.count() > 2:
            raise ValidationError("An animal can have at most 2 parents.")

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
        verbose_name='Animal',
    )
    medication_name = models.CharField(
        verbose_name='Medication Name',
        max_length=200,
    )
    dosage = models.CharField(
        verbose_name='Dosage',
        max_length=100,
    )
    frequency = models.CharField(
        verbose_name='Frequency of administration',
        max_length=100,
    )
    start_date = models.DateField(
        verbose_name='Start Date',
    )
    end_date = models.DateField(
        verbose_name='End Date',
        null=True,
        blank=True,
    )
    reason = models.TextField(
        verbose_name='Reason for prescription',
    )
    notes = models.TextField(
        verbose_name='Notes',
        blank=True,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='prescribed_medications',
        verbose_name='Prescribed by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Prescribed Medication'
        verbose_name_plural = 'Prescribed Medications'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.medication_name} - {self.animal.name}'


class Vaccination(models.Model):
    """Vaccination record for an animal."""
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='vaccinations',
        verbose_name='Animal',
    )
    vaccine_name = models.CharField(
        verbose_name='Vaccine Name',
        max_length=200,
    )
    vaccine_for = models.CharField(
        verbose_name='Vaccine For',
        max_length=200,
    )
    vaccine_batch_number = models.CharField(
        verbose_name='Batch Number',
        max_length=100,
    )
    vaccination_date = models.DateField(
        verbose_name='Vaccination Date',
    )
    expiration_date = models.DateField(
        verbose_name='Expiration Date',
    )
    next_due_date = models.DateField(
        verbose_name='Next Due Date',
        null=True,
        blank=True,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='administered_vaccinations',
        verbose_name='Performed by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vaccination'
        verbose_name_plural = 'Vaccinations'
        ordering = ['-vaccination_date']

    def __str__(self):
        return f'{self.vaccine_name} - {self.animal.name}'


class MedicalProcedure(models.Model):
    """Medical procedure record for an animal."""
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='procedures',
        verbose_name='Animal',
    )
    procedure_date = models.DateField(
        verbose_name='Procedure Date',
    )
    description = models.TextField(
        verbose_name='Description',
    )
    result = models.TextField(
        verbose_name='Result/Progress',
    )
    cost = models.DecimalField(
        verbose_name='Cost',
        max_digits=10,
        decimal_places=2,
    )
    notes = models.TextField(
        verbose_name='Notes',
        blank=True,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_procedures',
        verbose_name='Performed by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Medical Procedure'
        verbose_name_plural = 'Medical Procedures'
        ordering = ['-procedure_date']

    def __str__(self):
        return f'{self.description[:50]} - {self.animal.name}'
    

class Intake(models.Model):
    """Animal intake record."""
    intake_id = models.CharField(
        verbose_name='Intake Identifier',
        max_length=50,
        unique=True,
        default=uuid.uuid4,  
        editable=False,
    )
    animal = models.ForeignKey(
        Animal, 
        on_delete=models.CASCADE,
        related_name='intakes',
        verbose_name='Animal',  
    )
    intake_date = models.DateField(
        verbose_name='Intake Date',
        default=date.today
    )
    animal_condition = models.CharField(
        verbose_name='Animal Condition',
        max_length=255,
    )
    location = models.CharField(
        verbose_name='Location',
        max_length=255,
    )
    notes = models.CharField(
        verbose_name='Notes',
        max_length=255,
    )
    intake_type = models.CharField(
        verbose_name='Intake Type',
        max_length=20,
        choices=IntakeType.choices,
    )
    source_type = models.CharField(
        verbose_name='Source Type',
        max_length=20,
        choices = (("person", "person"), ("institution", "institution")),
        null = True,
        blank = True,
    )
    source_id = models.UUIDField(
        verbose_name='Source Identifier', 
        null = True,
        blank = True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Intake'
        verbose_name_plural = 'Intakes'
        ordering = ['-intake_date', '-intake_type']

    def __str__(self):
        return f'{self.animal.name} - {self.intake_date} - {self.get_intake_type_display()}'
    


class Photo(models.Model):
    """Photos for animals."""
    photo_id = models.CharField(
        verbose_name='Photo Identifier',
        max_length=50,
        unique=True,  
        editable=False,
        default=uuid.uuid4,
    )

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Animal',
    )

    url = models.CharField(
        verbose_name='URL',
        max_length=255,
    )
    filename = models.CharField(
        verbose_name='Filename',
        max_length=100,
    )
    upload_date = models.DateField(
        verbose_name='Upload Date',
        auto_now_add=True,
    )
    is_identification_photo = models.BooleanField(
        verbose_name='Is Identification Photo', 
        default=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        ordering = ['-created_at']
    def __str__(self):
        return self.photo_id