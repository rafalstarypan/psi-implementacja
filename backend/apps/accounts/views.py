"""
Views for accounts app.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import CurrentUserSerializer


class CurrentUserView(APIView):
    """
    API endpoint for getting current authenticated user's information.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return current user's data."""
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)
