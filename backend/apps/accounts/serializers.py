"""
Serializers for accounts app.
"""
from rest_framework import serializers
from .models import User, Role


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - full details."""
    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'role_display',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for User - for references in other models."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']


class CurrentUserSerializer(serializers.ModelSerializer):
    """Serializer for current authenticated user."""
    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'role_display',
        ]
        read_only_fields = fields
