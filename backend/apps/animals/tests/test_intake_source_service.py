import pytest
from unittest.mock import patch, Mock
from apps.animals.services.intake_source_service import SourceService

@pytest.fixture
def mock_context():
    """Tworzy przykładowy kontekst z obiektem request."""
    request = Mock()
    request.META = {'HTTP_AUTHORIZATION': 'Bearer user-token-123'}
    return {'request': request}

class TestSourceServiceHelpers:
    """Testy metod pomocniczych (_get_auth_headers, _detail_url)."""

    def test_detail_url_person(self):
        """Test generowania URL dla osoby."""
        url_list = SourceService._detail_url('person')
        assert url_list == 'http://localhost:8000/api/parties/persons/'
        
        url_detail = SourceService._detail_url('person', 123)
        assert url_detail == 'http://localhost:8000/api/parties/persons/123/'

    def test_detail_url_institution(self):
        """Test generowania URL dla instytucji."""
        url_list = SourceService._detail_url('institution')
        assert url_list == 'http://localhost:8000/api/parties/institutions/'
        
        url_detail = SourceService._detail_url('institution', 456)
        assert url_detail == 'http://localhost:8000/api/parties/institutions/456/'

    def test_auth_headers_from_settings(self, settings):
        """Test pobierania tokena z ustawień, gdy brak kontekstu."""
        # Używamy fixtury settings zamiast dekoratora
        settings.INTERNAL_SERVICE_TOKEN = 'secret-server-token'
        
        headers = SourceService._get_auth_headers(context=None)
        assert headers['Authorization'] == 'Bearer secret-server-token'

    def test_auth_headers_from_request(self, mock_context):
        """Test pobierania tokena z nagłówka żądania użytkownika."""
        headers = SourceService._get_auth_headers(context=mock_context)
        assert headers['Authorization'] == 'Bearer user-token-123'


class TestSourceServiceExists:
    """Testy metody exists."""

    @pytest.fixture(autouse=True)
    def setup_settings(self, settings):
        """Automatycznie ustawia token dla wszystkich testów w tej klasie."""
        settings.INTERNAL_SERVICE_TOKEN = 'test-token'

    @patch('apps.animals.services.intake_source_service.requests.get')
    def test_exists_returns_true_on_200(self, mock_get):
        """Powinien zwrócić True, gdy API odpowiada kodem 200."""
        mock_get.return_value.status_code = 200
        
        exists = SourceService.exists('person', 1)
        
        assert exists is True
        mock_get.assert_called_once()

    @patch('apps.animals.services.intake_source_service.requests.get')
    def test_exists_returns_false_on_404(self, mock_get):
        """Powinien zwrócić False, gdy API odpowiada kodem 404."""
        mock_get.return_value.status_code = 404
        
        exists = SourceService.exists('person', 999)
        
        assert exists is False

    @patch('apps.animals.services.intake_source_service.requests.get')
    def test_exists_passes_correct_params(self, mock_get, mock_context):
        """Sprawdza czy URL i nagłówki są poprawnie przekazywane."""
        mock_get.return_value.status_code = 200
        
        SourceService.exists('institution', 5, context=mock_context)
        
        args, kwargs = mock_get.call_args
        assert args[0] == 'http://localhost:8000/api/parties/institutions/5/'
        assert kwargs['headers']['Authorization'] == 'Bearer user-token-123'


class TestSourceServiceCreate:
    """Testy metody create."""

    @pytest.fixture(autouse=True)
    def setup_settings(self, settings):
        """Automatycznie ustawia token dla wszystkich testów w tej klasie."""
        settings.INTERNAL_SERVICE_TOKEN = 'test-token'

    @patch('apps.animals.services.intake_source_service.requests.post')
    def test_create_person_success(self, mock_post):
        """Test udanego utworzenia osoby (zwraca person_id)."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'person_id': 10, 'name': 'Jan'}
        mock_post.return_value = mock_response

        payload = {'first_name': 'Jan', 'last_name': 'Kowalski'}
        result_id = SourceService.create('person', payload)

        assert result_id == 10
        
        # Sprawdzamy, czy użyto tokena z ustawień (test-token)
        mock_post.assert_called_with(
            'http://localhost:8000/api/parties/persons/',
            json=payload,
            headers={'Authorization': 'Bearer test-token'},
            timeout=3
        )

    @patch('apps.animals.services.intake_source_service.requests.post')
    def test_create_institution_success(self, mock_post):
        """Test udanego utworzenia instytucji (zwraca institution_id)."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'institution_id': 50, 'name': 'Schronisko'}
        mock_post.return_value = mock_response

        payload = {'name': 'Schronisko'}
        result_id = SourceService.create('institution', payload)

        assert result_id == 50

    @patch('apps.animals.services.intake_source_service.requests.post')
    def test_create_failure_raises_exception(self, mock_post):
        """Test błędu API (nie 201) -> rzuca wyjątek."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        payload = {'invalid': 'data'}
        
        with pytest.raises(Exception) as excinfo:
            SourceService.create('person', payload)
        
        assert "Source creation failed" in str(excinfo.value)