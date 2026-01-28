from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Address, Person, Institution
from .serializers import AddressSerializer, PersonSerializer, InstitutionSerializer


# Create your views here.
class AddressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and creating addresses.
    """
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['city', 'postal_code']

    @action(detail=False, methods=['post'])
    def create_address(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            address = serializer.save()
            return Response(
                AddressSerializer(address).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and creating persons.
    """
    queryset = Person.objects.select_related('address')
    serializer_class = PersonSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['firstname', 'lastname']

    @action(detail=False, methods=['post'])
    def create_person(self, request):
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            person = serializer.save()
            return Response(
                PersonSerializer(person).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and creating institutions.
    """
    queryset = Institution.objects.select_related('address')
    serializer_class = InstitutionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

    @action(detail=False, methods=['post'])
    def create_institution(self, request):
        serializer = InstitutionSerializer(data=request.data)
        if serializer.is_valid():
            institution = serializer.save()
            return Response(
                InstitutionSerializer(institution).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
