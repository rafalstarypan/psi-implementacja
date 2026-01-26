"""
Views for animals app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from apps.accounts.permissions import IsEmployee
from apps.accounts.models import User, Role
from .models import Animal, Medication, Vaccination, MedicalProcedure
from .serializers import (
    AnimalListSerializer,
    AnimalDetailSerializer,
    MedicationSerializer,
    MedicationCreateSerializer,
    VaccinationSerializer,
    VaccinationCreateSerializer,
    MedicalProcedureSerializer,
    MedicalProcedureCreateSerializer,
    VeterinarianSerializer,
)


class AnimalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing animals.

    list: Get all animals with optional filtering and search.
    retrieve: Get detailed information about a single animal.
    """
    permission_classes = [IsEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['species', 'status', 'sex']
    search_fields = ['name', 'animal_id', 'breed']
    ordering_fields = ['name', 'intake_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Animal.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AnimalDetailSerializer
        return AnimalListSerializer

    @action(detail=True, methods=['get', 'post'])
    def medications(self, request, pk=None):
        """Get or create medications for an animal."""
        animal = self.get_object()

        if request.method == 'GET':
            medications = animal.medications.select_related('performed_by').all()
            page = self.paginate_queryset(medications)
            if page is not None:
                serializer = MedicationSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = MedicationSerializer(medications, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = MedicationCreateSerializer(
                data=request.data,
                context={'request': request, 'animal': animal}
            )
            if serializer.is_valid():
                medication = serializer.save()
                return Response(
                    MedicationSerializer(medication).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def vaccinations(self, request, pk=None):
        """Get or create vaccinations for an animal."""
        animal = self.get_object()

        if request.method == 'GET':
            vaccinations = animal.vaccinations.select_related('performed_by').all()
            page = self.paginate_queryset(vaccinations)
            if page is not None:
                serializer = VaccinationSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = VaccinationSerializer(vaccinations, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = VaccinationCreateSerializer(
                data=request.data,
                context={'request': request, 'animal': animal}
            )
            if serializer.is_valid():
                vaccination = serializer.save()
                return Response(
                    VaccinationSerializer(vaccination).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def procedures(self, request, pk=None):
        """Get or create medical procedures for an animal."""
        animal = self.get_object()

        if request.method == 'GET':
            procedures = animal.procedures.select_related('performed_by').all()
            page = self.paginate_queryset(procedures)
            if page is not None:
                serializer = MedicalProcedureSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = MedicalProcedureSerializer(procedures, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = MedicalProcedureCreateSerializer(
                data=request.data,
                context={'request': request, 'animal': animal}
            )
            if serializer.is_valid():
                procedure = serializer.save()
                return Response(
                    MedicalProcedureSerializer(procedure).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VeterinarianListView(APIView):
    """
    API endpoint for listing veterinarians (employees).
    Used in dropdowns when selecting who performed medical procedures.
    """
    permission_classes = [IsEmployee]

    def get(self, request):
        veterinarians = User.objects.filter(role=Role.EMPLOYEE, is_active=True)
        serializer = VeterinarianSerializer(veterinarians, many=True)
        return Response(serializer.data)
