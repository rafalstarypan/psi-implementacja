"""
Pytest fixtures for supplies app tests.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from rest_framework.test import APIClient
from apps.accounts.models import User, Role
from apps.supplies.models import (
    SupplyCategory, UnitOfMeasure, Supplier, SupplyItem,
    Inventory, InventoryLog, SupplyOrder, SupplyOrderLine,
    InventoryOperationType, SupplyOrderStatus
)


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def employee_user(db):
    """Create and return an employee user."""
    return User.objects.create_user(
        email='pracownik@schronisko.pl',
        password='haslo123',
        first_name='Jan',
        last_name='Kowalski',
        role=Role.EMPLOYEE,
    )


@pytest.fixture
def volunteer_user(db):
    """Create and return a volunteer user."""
    return User.objects.create_user(
        email='wolontariusz@schronisko.pl',
        password='haslo123',
        first_name='Anna',
        last_name='Nowak',
        role=Role.VOLUNTEER,
    )


@pytest.fixture
def authenticated_employee(api_client, employee_user):
    """Return an API client authenticated as an employee."""
    api_client.force_authenticate(user=employee_user)
    return api_client


@pytest.fixture
def authenticated_volunteer(api_client, volunteer_user):
    """Return an API client authenticated as a volunteer."""
    api_client.force_authenticate(user=volunteer_user)
    return api_client


@pytest.fixture
def category_food(db):
    """Create food category."""
    return SupplyCategory.objects.create(name='Żywność')


@pytest.fixture
def category_medicine(db):
    """Create medicine category."""
    return SupplyCategory.objects.create(name='Leki')


@pytest.fixture
def category_hygiene(db):
    """Create hygiene category."""
    return SupplyCategory.objects.create(name='Higiena')


@pytest.fixture
def unit_kg(db):
    """Create kilogram unit."""
    return UnitOfMeasure.objects.create(name='kilogram', abbreviation='kg')


@pytest.fixture
def unit_pcs(db):
    """Create pieces unit."""
    return UnitOfMeasure.objects.create(name='sztuka', abbreviation='szt')


@pytest.fixture
def supplier(db):
    """Create a supplier."""
    return Supplier.objects.create(
        name='PetFood Sp. z o.o.',
        phone_number='123456789',
        email='kontakt@petfood.pl'
    )


@pytest.fixture
def supply_item_dog_food(db, category_food, unit_kg):
    """Create dog food supply item with inventory."""
    item = SupplyItem.objects.create(
        name='Karma sucha dla psów',
        description='Karma sucha dla psów dorosłych',
        min_stock=Decimal('50.00'),
        category=category_food,
        unit=unit_kg,
    )
    Inventory.objects.create(
        supply_item=item,
        current_quantity=Decimal('35.00'),
    )
    return item


@pytest.fixture
def supply_item_cat_food(db, category_food, unit_pcs):
    """Create cat food supply item with inventory."""
    item = SupplyItem.objects.create(
        name='Karma mokra dla kotów',
        description='Karma mokra w puszkach',
        min_stock=Decimal('80.00'),
        category=category_food,
        unit=unit_pcs,
    )
    Inventory.objects.create(
        supply_item=item,
        current_quantity=Decimal('120.00'),
    )
    return item


@pytest.fixture
def supply_item_antibiotics(db, category_medicine, unit_pcs):
    """Create antibiotics supply item with inventory (low stock)."""
    item = SupplyItem.objects.create(
        name='Antybiotyki',
        description='Antybiotyki szerokopasmowe',
        min_stock=Decimal('20.00'),
        category=category_medicine,
        unit=unit_pcs,
    )
    Inventory.objects.create(
        supply_item=item,
        current_quantity=Decimal('5.00'),  # Low stock (25%)
    )
    return item


@pytest.fixture
def supply_items(supply_item_dog_food, supply_item_cat_food, supply_item_antibiotics):
    """Return all supply items."""
    return [supply_item_dog_food, supply_item_cat_food, supply_item_antibiotics]


@pytest.fixture
def pending_order(db, supplier, supply_item_dog_food):
    """Create a pending supply order."""
    order = SupplyOrder.objects.create(
        supplier=supplier,
        expected_delivery_date=date.today() + timedelta(days=7),
        status=SupplyOrderStatus.IN_PROGRESS,
    )
    SupplyOrderLine.objects.create(
        order=order,
        supply_item=supply_item_dog_food,
        quantity=Decimal('30.00'),
    )
    return order


@pytest.fixture
def inventory_logs(db, supply_item_dog_food, employee_user):
    """Create inventory logs for dog food."""
    inventory = supply_item_dog_food.inventory
    logs = [
        InventoryLog.objects.create(
            inventory=inventory,
            operation_type=InventoryOperationType.OUTBOUND,
            quantity=Decimal('10.00'),
            comment='Karmienie poranne',
            performed_by=employee_user,
        ),
        InventoryLog.objects.create(
            inventory=inventory,
            operation_type=InventoryOperationType.INBOUND,
            quantity=Decimal('50.00'),
            comment='Dostawa od PetFood',
            performed_by=employee_user,
        ),
    ]
    return logs
