"""
Models for accounts app - User authentication and roles.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.TextChoices):
    """User roles in the shelter system."""
    EMPLOYEE = 'employee', 'Pracownik'
    VOLUNTEER = 'volunteer', 'Wolontariusz'
    VISITOR = 'visitor', 'Odwiedzający'


class UserManager(BaseUserManager):
    """Custom user manager for User model."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('Email jest wymagany')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Role.EMPLOYEE)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the shelter system.
    Uses email as the unique identifier instead of username.
    """
    email = models.EmailField(
        verbose_name='Adres email',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Imię',
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name='Nazwisko',
        max_length=100,
    )
    role = models.CharField(
        verbose_name='Rola',
        max_length=20,
        choices=Role.choices,
        default=Role.VISITOR,
    )
    is_active = models.BooleanField(
        verbose_name='Aktywny',
        default=True,
    )
    is_staff = models.BooleanField(
        verbose_name='Dostęp do panelu admina',
        default=False,
    )
    created_at = models.DateTimeField(
        verbose_name='Data utworzenia',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name='Data aktualizacji',
        auto_now=True,
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Użytkownik'
        verbose_name_plural = 'Użytkownicy'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return full name of the user."""
        return f'{self.first_name} {self.last_name}'

    def is_employee(self):
        """Check if user is an employee."""
        return self.role == Role.EMPLOYEE

    def is_volunteer(self):
        """Check if user is a volunteer."""
        return self.role == Role.VOLUNTEER

    def is_visitor(self):
        """Check if user is a visitor."""
        return self.role == Role.VISITOR
