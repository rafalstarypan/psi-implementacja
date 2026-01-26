"""
Tests for accounts views.
"""
import pytest
from django.urls import reverse
from apps.accounts.models import Role


@pytest.mark.django_db
class TestCurrentUserView:
    """Tests for CurrentUserView."""

    def test_get_current_user_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot access the endpoint."""
        url = reverse('accounts:current-user')
        response = api_client.get(url)

        assert response.status_code == 401

    def test_get_current_user_employee(self, authenticated_employee, employee_user):
        """Test getting current user data for employee."""
        url = reverse('accounts:current-user')
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert response.data['email'] == employee_user.email
        assert response.data['first_name'] == employee_user.first_name
        assert response.data['last_name'] == employee_user.last_name
        assert response.data['role'] == Role.EMPLOYEE
        assert response.data['role_display'] == 'Pracownik'
        assert response.data['full_name'] == employee_user.full_name

    def test_get_current_user_volunteer(self, authenticated_volunteer, volunteer_user):
        """Test getting current user data for volunteer."""
        url = reverse('accounts:current-user')
        response = authenticated_volunteer.get(url)

        assert response.status_code == 200
        assert response.data['email'] == volunteer_user.email
        assert response.data['role'] == Role.VOLUNTEER
        assert response.data['role_display'] == 'Wolontariusz'

    def test_get_current_user_visitor(self, authenticated_visitor, visitor_user):
        """Test getting current user data for visitor."""
        url = reverse('accounts:current-user')
        response = authenticated_visitor.get(url)

        assert response.status_code == 200
        assert response.data['email'] == visitor_user.email
        assert response.data['role'] == Role.VISITOR
        assert response.data['role_display'] == 'Odwiedzający'
