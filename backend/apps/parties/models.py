import uuid
from django.db import models
from django.core.validators import RegexValidator

postal_code_validator = RegexValidator(
    regex=r'^\d{2}-\d{3}$',
    message='Postal code must be in format: XX-XXX'
)

class Address(models.Model):
    """Person or institutions address."""
    address_id = models.CharField(
        verbose_name='Address Identifier',
        max_length=50,
        unique=True,
        default=uuid.uuid4,  
        editable=False,
    )
    city = models.CharField(
        verbose_name='City',
        max_length=50,
    )
    postal_code = models.CharField(
        verbose_name='Postal Code',
        max_length=10,
        validators=[postal_code_validator],
    )
    street = models.CharField(
        verbose_name='Street',
        max_length=50,
    )
    building_number = models.CharField(
        verbose_name='Building Number',
        max_length=5,
    )
    apartment_number = models.CharField(
        verbose_name='Apartment Number',
        max_length=5,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-city', '-street', '-building_number']

    def __str__(self):
        return f'{self.city} {self.postal_code} {self.street} {self.building_number} {self.apartment_number}'



class Person(models.Model):
    """Person who interacts with the shelter."""
    person_id = models.CharField(
        verbose_name='Person Identifier',
        max_length=50,
        unique=True,
        default=uuid.uuid4,  
        editable=False,
    )
    phone_number = models.CharField(
        verbose_name='Phone Number',
        max_length=15,
    )
    email_address = models.CharField(
        verbose_name='Email Address',
        max_length=50,
        blank=True,
    )
    address = models.ForeignKey(
        Address,        
        verbose_name='Address',
        on_delete=models.SET_NULL,
        related_name='persons',
        null=True,
    )   
    firstname = models.CharField(
        verbose_name='First Name',
        max_length=100,
    )
    lastname = models.CharField(
        verbose_name='Last Name',
        max_length=100,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'People'
        ordering = ['-firstname', '-lastname']

    def __str__(self):
        return f'{self.person_id} {self.firstname} {self.lastname}'
    

class Institution(models.Model):
    """Institution which interacts with the shelter."""
    institution_id = models.CharField(
        verbose_name='Institution Identifier',
        max_length=50,
        unique=True,
        default=uuid.uuid4,  
        editable=False,
    )
    phone_number = models.CharField(
        verbose_name='Phone Number',
        max_length=15,
    )
    email_address = models.CharField(
        verbose_name='Email Address',
        max_length=50,
        blank=True,
    )
    address = models.ForeignKey(
        Address,        
        verbose_name='Address',
        on_delete=models.SET_NULL,
        related_name='institutions',
        null=True,
    )
    name = models.CharField(
        verbose_name='Name',
        max_length=100,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'
        ordering = ['-name']

    def __str__(self):
        return f'{self.institution_id} {self.name}'