from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.pagination import PageNumberPagination

from .models import Address, Person, Institution
from .serializers import AddressSerializer, PersonListSerializer, PersonDetailSerializer, PersonCreateSerializer, InstitutionListSerializer, InstitutionDetailSerializer, InstitutionCreateSerializer



class PartyPagination(PageNumberPagination):
    page_size = 5   
    page_size_query_param = 'page_size'
    max_page_size = 50


class PersonViewSet(viewsets.ModelViewSet):

    pagination_class = PartyPagination
    queryset = Person.objects.all()
    lookup_field = 'person_id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PersonDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return PersonCreateSerializer
        return PersonListSerializer



class InstitutionViewSet(viewsets.ModelViewSet):

    pagination_class = PartyPagination
    queryset = Institution.objects.all()
    lookup_field = 'institution_id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InstitutionDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return InstitutionCreateSerializer
        return InstitutionListSerializer







