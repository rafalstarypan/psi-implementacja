"""
Custom permissions for the shelter system.
"""
from rest_framework.permissions import BasePermission
from .models import Role


class IsEmployee(BasePermission):
    """
    Permission class that allows access only to employees.
    """
    message = 'Dostęp tylko dla pracowników schroniska.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == Role.EMPLOYEE
        )


class IsEmployeeOrVolunteer(BasePermission):
    """
    Permission class that allows access to employees and volunteers.
    """
    message = 'Dostęp tylko dla pracowników i wolontariuszy schroniska.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [Role.EMPLOYEE, Role.VOLUNTEER]
        )


class IsEmployeeOrReadOnly(BasePermission):
    """
    Permission class that allows read access to all authenticated users,
    but write access only to employees.
    """
    message = 'Tylko pracownicy mogą modyfikować te dane.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        return request.user.role == Role.EMPLOYEE
