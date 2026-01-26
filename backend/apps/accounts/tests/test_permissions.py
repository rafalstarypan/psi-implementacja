"""
Tests for accounts permissions.
"""
import pytest
from unittest.mock import Mock
from apps.accounts.models import User, Role
from apps.accounts.permissions import IsEmployee, IsEmployeeOrVolunteer, IsEmployeeOrReadOnly


@pytest.mark.django_db
class TestIsEmployeePermission:
    """Tests for IsEmployee permission."""

    def test_allows_employee(self, employee_user):
        """Test that employee has permission."""
        permission = IsEmployee()
        request = Mock()
        request.user = employee_user

        assert permission.has_permission(request, None) is True

    def test_denies_volunteer(self, volunteer_user):
        """Test that volunteer does not have permission."""
        permission = IsEmployee()
        request = Mock()
        request.user = volunteer_user

        assert permission.has_permission(request, None) is False

    def test_denies_visitor(self, visitor_user):
        """Test that visitor does not have permission."""
        permission = IsEmployee()
        request = Mock()
        request.user = visitor_user

        assert permission.has_permission(request, None) is False

    def test_denies_unauthenticated(self):
        """Test that unauthenticated user does not have permission."""
        permission = IsEmployee()
        request = Mock()
        request.user = Mock(is_authenticated=False)

        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsEmployeeOrVolunteerPermission:
    """Tests for IsEmployeeOrVolunteer permission."""

    def test_allows_employee(self, employee_user):
        """Test that employee has permission."""
        permission = IsEmployeeOrVolunteer()
        request = Mock()
        request.user = employee_user

        assert permission.has_permission(request, None) is True

    def test_allows_volunteer(self, volunteer_user):
        """Test that volunteer has permission."""
        permission = IsEmployeeOrVolunteer()
        request = Mock()
        request.user = volunteer_user

        assert permission.has_permission(request, None) is True

    def test_denies_visitor(self, visitor_user):
        """Test that visitor does not have permission."""
        permission = IsEmployeeOrVolunteer()
        request = Mock()
        request.user = visitor_user

        assert permission.has_permission(request, None) is False

    def test_denies_unauthenticated(self):
        """Test that unauthenticated user does not have permission."""
        permission = IsEmployeeOrVolunteer()
        request = Mock()
        request.user = Mock(is_authenticated=False)

        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsEmployeeOrReadOnlyPermission:
    """Tests for IsEmployeeOrReadOnly permission."""

    def test_allows_employee_read(self, employee_user):
        """Test that employee can read."""
        permission = IsEmployeeOrReadOnly()
        request = Mock()
        request.user = employee_user
        request.method = 'GET'

        assert permission.has_permission(request, None) is True

    def test_allows_employee_write(self, employee_user):
        """Test that employee can write."""
        permission = IsEmployeeOrReadOnly()
        request = Mock()
        request.user = employee_user
        request.method = 'POST'

        assert permission.has_permission(request, None) is True

    def test_allows_volunteer_read(self, volunteer_user):
        """Test that volunteer can read."""
        permission = IsEmployeeOrReadOnly()
        request = Mock()
        request.user = volunteer_user
        request.method = 'GET'

        assert permission.has_permission(request, None) is True

    def test_denies_volunteer_write(self, volunteer_user):
        """Test that volunteer cannot write."""
        permission = IsEmployeeOrReadOnly()
        request = Mock()
        request.user = volunteer_user
        request.method = 'POST'

        assert permission.has_permission(request, None) is False

    def test_allows_visitor_read(self, visitor_user):
        """Test that visitor can read."""
        permission = IsEmployeeOrReadOnly()
        request = Mock()
        request.user = visitor_user
        request.method = 'GET'

        assert permission.has_permission(request, None) is True

    def test_denies_visitor_write(self, visitor_user):
        """Test that visitor cannot write."""
        permission = IsEmployeeOrReadOnly()
        request = Mock()
        request.user = visitor_user
        request.method = 'POST'

        assert permission.has_permission(request, None) is False

    def test_denies_unauthenticated(self):
        """Test that unauthenticated user cannot access."""
        permission = IsEmployeeOrReadOnly()
        request = Mock()
        request.user = Mock(is_authenticated=False)
        request.method = 'GET'

        assert permission.has_permission(request, None) is False
