import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.parties.models import Person, Institution, Address

# Pobieramy model użytkownika zdefiniowany w projekcie
User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_user(db):
    """
    Tworzy przykładowego użytkownika do testów.
    Poprawka: Usunięto parametr 'username', ponieważ model User go nie posiada.
    """
    email = 'test_parties@example.com'
    password = 'password'
    
    # Próbujemy użyć create_user (standard dla hashowania hasła)
    if hasattr(User.objects, 'create_user'):
        return User.objects.create_user(email=email, password=password)
    else:
        # Fallback dla prostych modeli bez menedżera create_user
        return User.objects.create(email=email, password=password)

@pytest.fixture
def auth_client(api_client, sample_user):
    """Zwraca klienta API zalogowanego jako sample_user."""
    api_client.force_authenticate(user=sample_user)
    return api_client

@pytest.fixture
def sample_address():
    return Address.objects.create(
        city='Wrocław',
        postal_code='50-100',
        street='Rynek',
        building_number='1',
        apartment_number='2'
    )

@pytest.fixture
def sample_person(sample_address):
    return Person.objects.create(
        firstname='Jan',
        lastname='Kowalski',
        phone_number='123456789',
        email_address='jan.kowalski@example.com',
        address=sample_address
    )

@pytest.fixture
def sample_institution(sample_address):
    return Institution.objects.create(
        name='Fundacja Pomocy',
        phone_number='987654321',
        email_address='kontakt@fundacja.pl',
        address=sample_address
    )


@pytest.mark.django_db
class TestPersonViewSet:
    """Testy dla PersonViewSet."""

    def test_list_persons_pagination(self, auth_client, sample_address):
        """Sprawdza listowanie osób i paginację (page_size=5)."""
        # Tworzymy 6 osób, aby wymusić drugą stronę
        for i in range(6):
            Person.objects.create(
                firstname=f'Person_{i}',
                lastname='Test',
                phone_number=f'123{i}',
                email_address=f'test{i}@example.com',
                address=sample_address
            )

        url = reverse('parties:person-list')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        assert response.data['count'] == 6
        assert response.data['next'] is not None

    def test_list_serializer_fields(self, auth_client, sample_person):
        """Sprawdza, czy widok listy używa PersonListSerializer (okrojone pola)."""
        url = reverse('parties:person-list')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        person_data = response.data['results'][0]
        
        assert 'firstname' in person_data
        assert 'person_id' in person_data
        assert 'phone_number' not in person_data
        assert 'address' not in person_data

    def test_retrieve_person_detail(self, auth_client, sample_person):
        """Sprawdza pobieranie szczegółów (lookup po person_id)."""
        url = reverse('parties:person-detail', kwargs={'person_id': sample_person.person_id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['firstname'] == sample_person.firstname
        assert response.data['phone_number'] == sample_person.phone_number
        assert response.data['address']['city'] == sample_person.address.city

    def test_create_person_with_address(self, auth_client):
        """Sprawdza tworzenie osoby z zagnieżdżonym adresem."""
        url = reverse('parties:person-list')
        payload = {
            'firstname': 'Adam',
            'lastname': 'Nowak',
            'email_address': 'adam@nowak.pl',
            'phone_number': '555666777',
            'address': {
                'city': 'Gdańsk',
                'postal_code': '80-001',
                'street': 'Długa',
                'building_number': '10',
                'apartment_number': ''
            }
        }

        response = auth_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Person.objects.count() == 1
        assert Address.objects.count() == 1
        
        person = Person.objects.first()
        assert person.firstname == 'Adam'
        assert person.address.city == 'Gdańsk'

    def test_create_person_validation_error(self, auth_client):
        """Sprawdza walidację (np. brak wymaganych pól)."""
        url = reverse('parties:person-list')
        payload = {
            'firstname': 'Adam',
        }
        response = auth_client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestInstitutionViewSet:
    """Testy dla InstitutionViewSet."""

    def test_list_institutions(self, auth_client, sample_institution):
        """Sprawdza listę instytucji i poprawne pola serializera."""
        url = reverse('parties:institution-list')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        
        data = response.data['results'][0]
        assert 'name' in data
        assert 'address' not in data 

    def test_retrieve_institution(self, auth_client, sample_institution):
        """Sprawdza szczegóły instytucji (lookup po institution_id)."""
        url = reverse('parties:institution-detail', kwargs={'institution_id': sample_institution.institution_id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Fundacja Pomocy'
        assert response.data['address']['city'] == 'Wrocław'

    def test_create_institution_nested(self, auth_client):
        """Sprawdza tworzenie instytucji z adresem."""
        url = reverse('parties:institution-list')
        payload = {
            'name': 'Schronisko Miejskie',
            'email_address': 'biuro@schronisko.pl',
            'phone_number': '111222333',
            'address': {
                'city': 'Kraków',
                'postal_code': '30-001',
                'street': 'Wawelska',
                'building_number': '5'
            }
        }

        response = auth_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Institution.objects.count() == 1
        
        inst = Institution.objects.get(name='Schronisko Miejskie')
        assert inst.address.city == 'Kraków'