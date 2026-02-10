import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.parties.models import Address, Person, Institution

@pytest.mark.django_db
class TestAddress:
    """Testy dla modelu Address."""

    def test_create_valid_address(self):
        """Sprawdza utworzenie poprawnego adresu."""
        address = Address(
            city='Warszawa',
            postal_code='00-001',
            street='Marszałkowska',
            building_number='10',
            apartment_number='5'
        )
        address.full_clean() 
        address.save()
        
        assert address.address_id is not None
        assert len(str(address.address_id)) > 0
        assert str(address) == 'Warszawa 00-001 Marszałkowska 10 5'

    def test_postal_code_valid_formats(self):
        """Sprawdza poprawne formaty kodu pocztowego."""
        valid_codes = ['12-345', '00-000', '99-999']
        for code in valid_codes:
            address = Address(
                city='Test', postal_code=code, street='Ulica', building_number='1'
            )
            address.full_clean()  

    def test_postal_code_invalid_formats(self):
        """Sprawdza błędne formaty kodu pocztowego (RegexValidator)."""
        invalid_codes = ['12345', '12-34', '12-3456', 'AB-CDE', '12 345']
        
        for code in invalid_codes:
            address = Address(
                city='Test', postal_code=code, street='Ulica', building_number='1'
            )
            with pytest.raises(ValidationError) as excinfo:
                address.full_clean()
            
            assert 'Postal code must be in format: XX-XXX' in str(excinfo.value)


@pytest.mark.django_db
class TestPerson:
    """Testy dla modelu Person."""

    @pytest.fixture
    def address(self):
        return Address.objects.create(
            city='Kraków', postal_code='30-001', street='Rynek', building_number='1'
        )

    def test_create_person(self, address):
        """Sprawdza utworzenie osoby z przypisanym adresem."""
        person = Person.objects.create(
            firstname='Jan',
            lastname='Kowalski',
            phone_number='123456789',
            email_address='jan@example.com',
            address=address
        )
        
        assert person.person_id is not None
        assert person.address == address
        assert str(person) == f'{person.person_id} Jan Kowalski'

    def test_email_unique_constraint(self):
        """Sprawdza unikalność adresu email."""
        Person.objects.create(
            firstname='Jan', lastname='A', email_address='unique@test.com'
        )
        
        with pytest.raises(IntegrityError):
            Person.objects.create(
                firstname='Anna', lastname='B', email_address='unique@test.com'
            )

    def test_blank_email_uniqueness_issue(self):
        """
        WAŻNE: Ponieważ email_address ma unique=True i NIE ma null=True,
        baza danych potraktuje pusty string ('') jako wartość, która musi być unikalna.
        To oznacza, że tylko jedna osoba może nie mieć emaila.
        Ten test dokumentuje to zachowanie.
        """
        Person.objects.create(firstname='Osoba1', lastname='Test', email_address='')
        
        with pytest.raises(IntegrityError):
            Person.objects.create(firstname='Osoba2', lastname='Test', email_address='')


@pytest.mark.django_db
class TestInstitution:
    """Testy dla modelu Institution."""

    @pytest.fixture
    def address(self):
        return Address.objects.create(
            city='Gdańsk', postal_code='80-001', street='Długa', building_number='5'
        )

    def test_create_institution(self, address):
        """Sprawdza utworzenie instytucji."""
        inst = Institution.objects.create(
            name='Fundacja XYZ',
            phone_number='987654321',
            email_address='kontakt@xyz.pl',
            address=address
        )
        
        assert inst.institution_id is not None
        assert inst.address == address
        assert str(inst) == f'{inst.institution_id} Fundacja XYZ'

    def test_institution_ordering(self):
        """Sprawdza sortowanie (ordering = ['-name'])."""
        i1 = Institution.objects.create(name='Alfa', email_address='a@a.pl')
        i2 = Institution.objects.create(name='Beta', email_address='b@b.pl')
        
        institutions = list(Institution.objects.all())
        assert institutions == [i2, i1]