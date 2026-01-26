"""
Tests for accounts models.
"""
import pytest
from django.db import IntegrityError
from apps.accounts.models import User, Role


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""

    def test_create_user_with_email(self):
        """Test creating a user with email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name='Test',
            last_name='User',
        )

        assert user.email == email
        assert user.check_password(password)
        assert user.role == Role.VISITOR  # default role
        assert user.is_active is True
        assert user.is_staff is False

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
        ]
        for email, expected in sample_emails:
            user = User.objects.create_user(
                email=email,
                password='test123',
                first_name='Test',
                last_name='User',
            )
            assert user.email == expected

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without email raises ValueError."""
        with pytest.raises(ValueError):
            User.objects.create_user(
                email='',
                password='test123',
                first_name='Test',
                last_name='User',
            )

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='test123',
            first_name='Admin',
            last_name='User',
        )

        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.role == Role.EMPLOYEE

    def test_user_email_unique(self):
        """Test that email must be unique."""
        User.objects.create_user(
            email='test@example.com',
            password='test123',
            first_name='Test',
            last_name='User',
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',
                password='test456',
                first_name='Test2',
                last_name='User2',
            )

    def test_user_full_name_property(self):
        """Test user full_name property."""
        user = User.objects.create_user(
            email='test@example.com',
            password='test123',
            first_name='Jan',
            last_name='Kowalski',
        )

        assert user.full_name == 'Jan Kowalski'

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='test123',
            first_name='Jan',
            last_name='Kowalski',
        )

        assert str(user) == 'test@example.com'

    def test_user_is_employee(self):
        """Test is_employee method."""
        employee = User.objects.create_user(
            email='employee@example.com',
            password='test123',
            first_name='Test',
            last_name='Employee',
            role=Role.EMPLOYEE,
        )
        volunteer = User.objects.create_user(
            email='volunteer@example.com',
            password='test123',
            first_name='Test',
            last_name='Volunteer',
            role=Role.VOLUNTEER,
        )

        assert employee.is_employee() is True
        assert volunteer.is_employee() is False

    def test_user_is_volunteer(self):
        """Test is_volunteer method."""
        volunteer = User.objects.create_user(
            email='volunteer@example.com',
            password='test123',
            first_name='Test',
            last_name='Volunteer',
            role=Role.VOLUNTEER,
        )
        employee = User.objects.create_user(
            email='employee@example.com',
            password='test123',
            first_name='Test',
            last_name='Employee',
            role=Role.EMPLOYEE,
        )

        assert volunteer.is_volunteer() is True
        assert employee.is_volunteer() is False

    def test_user_is_visitor(self):
        """Test is_visitor method."""
        visitor = User.objects.create_user(
            email='visitor@example.com',
            password='test123',
            first_name='Test',
            last_name='Visitor',
            role=Role.VISITOR,
        )
        employee = User.objects.create_user(
            email='employee@example.com',
            password='test123',
            first_name='Test',
            last_name='Employee',
            role=Role.EMPLOYEE,
        )

        assert visitor.is_visitor() is True
        assert employee.is_visitor() is False


@pytest.mark.django_db
class TestRole:
    """Tests for Role choices."""

    def test_role_choices_exist(self):
        """Test that all expected role choices exist."""
        assert Role.EMPLOYEE == 'employee'
        assert Role.VOLUNTEER == 'volunteer'
        assert Role.VISITOR == 'visitor'

    def test_role_labels(self):
        """Test role labels are in Polish."""
        labels = dict(Role.choices)
        assert labels[Role.EMPLOYEE] == 'Pracownik'
        assert labels[Role.VOLUNTEER] == 'Wolontariusz'
        assert labels[Role.VISITOR] == 'Odwiedzający'
