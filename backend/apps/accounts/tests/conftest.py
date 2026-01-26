"""
Pytest fixtures for accounts app tests.
"""
import pytest
from rest_framework.test import APIClient
from apps.accounts.models import User, Role


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
def visitor_user(db):
    """Create and return a visitor user."""
    return User.objects.create_user(
        email='odwiedzajacy@schronisko.pl',
        password='haslo123',
        first_name='Piotr',
        last_name='Wiśniewski',
        role=Role.VISITOR,
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
def authenticated_visitor(api_client, visitor_user):
    """Return an API client authenticated as a visitor."""
    api_client.force_authenticate(user=visitor_user)
    return api_client
