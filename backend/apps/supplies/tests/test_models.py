"""
Tests for supplies models.
"""
import pytest
from decimal import Decimal
from apps.supplies.models import (
    SupplyCategory, UnitOfMeasure, SupplyItem, Inventory,
    InventoryLog, InventoryOperationType
)


@pytest.mark.django_db
class TestSupplyCategory:
    """Tests for SupplyCategory model."""

    def test_create_category(self):
        """Test creating a supply category."""
        category = SupplyCategory.objects.create(name='Żywność')
        assert category.name == 'Żywność'
        assert str(category) == 'Żywność'

    def test_category_name_unique(self, category_food):
        """Test that category name must be unique."""
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            SupplyCategory.objects.create(name='Żywność')


@pytest.mark.django_db
class TestUnitOfMeasure:
    """Tests for UnitOfMeasure model."""

    def test_create_unit(self):
        """Test creating a unit of measure."""
        unit = UnitOfMeasure.objects.create(name='kilogram', abbreviation='kg')
        assert unit.name == 'kilogram'
        assert unit.abbreviation == 'kg'
        assert str(unit) == 'kilogram (kg)'


@pytest.mark.django_db
class TestSupplyItem:
    """Tests for SupplyItem model."""

    def test_create_supply_item(self, category_food, unit_kg):
        """Test creating a supply item."""
        item = SupplyItem.objects.create(
            name='Karma dla psów',
            description='Test description',
            min_stock=Decimal('50.00'),
            category=category_food,
            unit=unit_kg,
        )
        assert item.name == 'Karma dla psów'
        assert item.category == category_food
        assert item.unit == unit_kg
        assert str(item) == 'Karma dla psów'

    def test_current_quantity_with_inventory(self, supply_item_dog_food):
        """Test current_quantity property with inventory."""
        assert supply_item_dog_food.current_quantity == Decimal('35.00')

    def test_current_quantity_without_inventory(self, category_food, unit_kg):
        """Test current_quantity property without inventory."""
        item = SupplyItem.objects.create(
            name='New Item',
            min_stock=Decimal('10.00'),
            category=category_food,
            unit=unit_kg,
        )
        assert item.current_quantity == Decimal('0.00')

    def test_stock_status_good(self, supply_item_cat_food):
        """Test stock_status when quantity > min_stock."""
        # 120 / 80 = 150% - good
        assert supply_item_cat_food.stock_status == 'good'

    def test_stock_status_warning(self, supply_item_dog_food):
        """Test stock_status when quantity is between 50% and 100% of min_stock."""
        # 35 / 50 = 70% - warning
        assert supply_item_dog_food.stock_status == 'warning'

    def test_stock_status_low(self, supply_item_antibiotics):
        """Test stock_status when quantity < 50% of min_stock."""
        # 5 / 20 = 25% - low
        assert supply_item_antibiotics.stock_status == 'low'


@pytest.mark.django_db
class TestInventory:
    """Tests for Inventory model."""

    def test_create_inventory(self, supply_item_dog_food):
        """Test that inventory is created with supply item."""
        inventory = supply_item_dog_food.inventory
        assert inventory.current_quantity == Decimal('35.00')

    def test_inventory_str(self, supply_item_dog_food):
        """Test inventory string representation."""
        inventory = supply_item_dog_food.inventory
        assert str(inventory) == 'Karma sucha dla psów: 35.00 kg'


@pytest.mark.django_db
class TestInventoryLog:
    """Tests for InventoryLog model."""

    def test_create_inbound_log(self, supply_item_dog_food, employee_user):
        """Test creating an inbound inventory log."""
        log = InventoryLog.objects.create(
            inventory=supply_item_dog_food.inventory,
            operation_type=InventoryOperationType.INBOUND,
            quantity=Decimal('50.00'),
            comment='Dostawa',
            performed_by=employee_user,
        )
        assert log.operation_type == InventoryOperationType.INBOUND
        assert log.quantity == Decimal('50.00')
        assert str(log) == 'Karma sucha dla psów: +50.00'

    def test_create_outbound_log(self, supply_item_dog_food, employee_user):
        """Test creating an outbound inventory log."""
        log = InventoryLog.objects.create(
            inventory=supply_item_dog_food.inventory,
            operation_type=InventoryOperationType.OUTBOUND,
            quantity=Decimal('10.00'),
            comment='Karmienie',
            performed_by=employee_user,
        )
        assert log.operation_type == InventoryOperationType.OUTBOUND
        assert str(log) == 'Karma sucha dla psów: -10.00'

    def test_logs_ordered_by_timestamp_desc(self, inventory_logs):
        """Test that logs are ordered by timestamp descending."""
        logs = InventoryLog.objects.all()
        assert logs[0].timestamp >= logs[1].timestamp


@pytest.mark.django_db
class TestSupplyOrder:
    """Tests for SupplyOrder model."""

    def test_pending_order_created(self, pending_order, supplier, supply_item_dog_food):
        """Test creating a pending supply order."""
        assert pending_order.supplier == supplier
        assert pending_order.status == 'IN_PROGRESS'
        assert pending_order.lines.count() == 1
        assert pending_order.lines.first().supply_item == supply_item_dog_food
        assert pending_order.lines.first().quantity == Decimal('30.00')
