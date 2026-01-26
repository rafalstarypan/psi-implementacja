"""
Tests for supplies views.
"""
import pytest
from django.urls import reverse
from decimal import Decimal


@pytest.mark.django_db
class TestSupplyItemViewSet:
    """Tests for SupplyItemViewSet."""

    def test_list_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access the endpoint."""
        url = reverse('supplies:supply-item-list')
        response = api_client.get(url)
        assert response.status_code == 401

    def test_list_requires_employee_role(self, authenticated_volunteer):
        """Test that volunteers cannot access supply items."""
        url = reverse('supplies:supply-item-list')
        response = authenticated_volunteer.get(url)
        assert response.status_code == 403

    def test_list_returns_items_for_employee(self, authenticated_employee, supply_items):
        """Test that employees can list supply items."""
        url = reverse('supplies:supply-item-list')
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert len(response.data['results']) == len(supply_items)

    def test_list_search_by_name(self, authenticated_employee, supply_items):
        """Test searching supply items by name."""
        url = reverse('supplies:supply-item-list')
        response = authenticated_employee.get(url, {'search': 'karma'})

        assert response.status_code == 200
        # Should find both "Karma sucha dla psów" and "Karma mokra dla kotów"
        assert len(response.data['results']) == 2
        for item in response.data['results']:
            assert 'karma' in item['name'].lower()

    def test_list_filter_by_category(self, authenticated_employee, supply_items, category_food):
        """Test filtering supply items by category."""
        url = reverse('supplies:supply-item-list')
        response = authenticated_employee.get(url, {'category': category_food.id})

        assert response.status_code == 200
        assert len(response.data['results']) == 2  # Dog food and cat food
        for item in response.data['results']:
            assert item['category']['id'] == category_food.id

    def test_retrieve_item_details(self, authenticated_employee, supply_item_dog_food):
        """Test retrieving a single supply item."""
        url = reverse('supplies:supply-item-detail', kwargs={'pk': supply_item_dog_food.id})
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert response.data['id'] == supply_item_dog_food.id
        assert response.data['name'] == supply_item_dog_food.name
        assert Decimal(response.data['current_quantity']) == Decimal('35.00')
        assert response.data['stock_status'] == 'warning'

    def test_retrieve_item_with_pending_order(
        self, authenticated_employee, supply_item_dog_food, pending_order
    ):
        """Test that pending orders are included in item details."""
        url = reverse('supplies:supply-item-detail', kwargs={'pk': supply_item_dog_food.id})
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert len(response.data['pending_orders']) == 1
        assert Decimal(response.data['pending_orders'][0]['quantity']) == Decimal('30.00')

    def test_retrieve_item_with_logs(
        self, authenticated_employee, supply_item_dog_food, inventory_logs
    ):
        """Test that inventory logs are included in item details."""
        url = reverse('supplies:supply-item-detail', kwargs={'pk': supply_item_dog_food.id})
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert len(response.data['recent_logs']) == 2

    def test_logs_endpoint(self, authenticated_employee, supply_item_dog_food, inventory_logs):
        """Test getting logs for a specific supply item."""
        url = reverse('supplies:supply-item-logs', kwargs={'pk': supply_item_dog_food.id})
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert len(response.data['results']) == 2

    def test_next_delivery_in_list(
        self, authenticated_employee, supply_item_dog_food, pending_order
    ):
        """Test that next delivery info is included in list view."""
        url = reverse('supplies:supply-item-list')
        response = authenticated_employee.get(url, {'search': 'sucha'})

        assert response.status_code == 200
        assert len(response.data['results']) == 1
        item = response.data['results'][0]
        assert item['next_delivery'] is not None
        assert Decimal(item['next_delivery']['quantity']) == Decimal('30.00')


@pytest.mark.django_db
class TestSupplyCategoryViewSet:
    """Tests for SupplyCategoryViewSet."""

    def test_list_categories(self, authenticated_employee, category_food, category_medicine):
        """Test listing supply categories."""
        url = reverse('supplies:supply-category-list')
        response = authenticated_employee.get(url)

        assert response.status_code == 200
        assert len(response.data) >= 2

    def test_list_requires_employee(self, authenticated_volunteer):
        """Test that volunteers cannot access categories."""
        url = reverse('supplies:supply-category-list')
        response = authenticated_volunteer.get(url)
        assert response.status_code == 403
