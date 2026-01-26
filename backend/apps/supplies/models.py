"""
Models for supplies app - Inventory management.
"""
from django.db import models
from django.conf import settings
from decimal import Decimal


class SupplyCategory(models.Model):
    """Category for supply items (e.g., Food, Medicine, Hygiene)."""
    name = models.CharField(
        verbose_name='Nazwa kategorii',
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = 'Kategoria zaopatrzenia'
        verbose_name_plural = 'Kategorie zaopatrzenia'
        ordering = ['name']

    def __str__(self):
        return self.name


class UnitOfMeasure(models.Model):
    """Unit of measure for supply items (e.g., kg, szt, l)."""
    name = models.CharField(
        verbose_name='Nazwa jednostki',
        max_length=50,
    )
    abbreviation = models.CharField(
        verbose_name='Skrót',
        max_length=10,
    )

    class Meta:
        verbose_name = 'Jednostka miary'
        verbose_name_plural = 'Jednostki miary'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.abbreviation})'


class Supplier(models.Model):
    """Supplier/vendor for supply orders."""
    name = models.CharField(
        verbose_name='Nazwa dostawcy',
        max_length=200,
    )
    phone_number = models.CharField(
        verbose_name='Telefon',
        max_length=20,
        blank=True,
    )
    email = models.EmailField(
        verbose_name='Email',
        blank=True,
    )

    class Meta:
        verbose_name = 'Dostawca'
        verbose_name_plural = 'Dostawcy'
        ordering = ['name']

    def __str__(self):
        return self.name


class SupplyItem(models.Model):
    """Supply item in the inventory."""
    name = models.CharField(
        verbose_name='Nazwa zasobu',
        max_length=200,
        unique=True,
    )
    description = models.TextField(
        verbose_name='Opis',
        blank=True,
    )
    min_stock = models.DecimalField(
        verbose_name='Minimalny stan',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    category = models.ForeignKey(
        SupplyCategory,
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name='Kategoria',
    )
    unit = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name='Jednostka miary',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Zasób magazynowy'
        verbose_name_plural = 'Zasoby magazynowe'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def current_quantity(self):
        """Get current quantity from inventory."""
        try:
            return self.inventory.current_quantity
        except Inventory.DoesNotExist:
            return Decimal('0.00')

    @property
    def stock_status(self):
        """
        Calculate stock status based on current quantity vs min_stock.
        Returns: 'low', 'warning', or 'good'
        """
        if self.min_stock == 0:
            return 'good'

        percentage = (self.current_quantity / self.min_stock) * 100

        if percentage < 50:
            return 'low'
        elif percentage < 100:
            return 'warning'
        return 'good'


class Inventory(models.Model):
    """Current inventory state for a supply item."""
    supply_item = models.OneToOneField(
        SupplyItem,
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name='Zasób',
    )
    current_quantity = models.DecimalField(
        verbose_name='Aktualna ilość',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    expiration_date = models.DateField(
        verbose_name='Data ważności',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Stan magazynowy'
        verbose_name_plural = 'Stany magazynowe'

    def __str__(self):
        return f'{self.supply_item.name}: {self.current_quantity} {self.supply_item.unit.abbreviation}'


class InventoryOperationType(models.TextChoices):
    """Types of inventory operations."""
    INBOUND = 'IN', 'Przyjęcie'
    OUTBOUND = 'OUT', 'Wydanie'


class InventoryLog(models.Model):
    """Log of inventory operations (inbound/outbound)."""
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Stan magazynowy',
    )
    operation_type = models.CharField(
        verbose_name='Typ operacji',
        max_length=3,
        choices=InventoryOperationType.choices,
    )
    quantity = models.DecimalField(
        verbose_name='Ilość',
        max_digits=10,
        decimal_places=2,
    )
    comment = models.TextField(
        verbose_name='Komentarz/Powód',
        blank=True,
    )
    timestamp = models.DateTimeField(
        verbose_name='Data i godzina',
        auto_now_add=True,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_logs',
        verbose_name='Wykonał',
    )

    class Meta:
        verbose_name = 'Operacja magazynowa'
        verbose_name_plural = 'Operacje magazynowe'
        ordering = ['-timestamp']

    def __str__(self):
        sign = '+' if self.operation_type == InventoryOperationType.INBOUND else '-'
        return f'{self.inventory.supply_item.name}: {sign}{self.quantity}'


class SupplyOrderStatus(models.TextChoices):
    """Status of supply orders."""
    IN_PROGRESS = 'IN_PROGRESS', 'W realizacji'
    COMPLETED = 'COMPLETED', 'Zrealizowane'
    CANCELLED = 'CANCELLED', 'Anulowane'


class SupplyOrder(models.Model):
    """Order for supplies from a supplier."""
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Dostawca',
    )
    issue_date = models.DateTimeField(
        verbose_name='Data złożenia',
        auto_now_add=True,
    )
    expected_delivery_date = models.DateField(
        verbose_name='Oczekiwana data dostawy',
    )
    status = models.CharField(
        verbose_name='Status',
        max_length=20,
        choices=SupplyOrderStatus.choices,
        default=SupplyOrderStatus.IN_PROGRESS,
    )
    notes = models.TextField(
        verbose_name='Uwagi',
        blank=True,
    )

    class Meta:
        verbose_name = 'Zamówienie zaopatrzenia'
        verbose_name_plural = 'Zamówienia zaopatrzenia'
        ordering = ['-issue_date']

    def __str__(self):
        return f'Zamówienie #{self.id} - {self.supplier.name}'


class SupplyOrderLine(models.Model):
    """Line item in a supply order."""
    order = models.ForeignKey(
        SupplyOrder,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Zamówienie',
    )
    supply_item = models.ForeignKey(
        SupplyItem,
        on_delete=models.PROTECT,
        related_name='order_lines',
        verbose_name='Zasób',
    )
    quantity = models.DecimalField(
        verbose_name='Ilość',
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = 'Pozycja zamówienia'
        verbose_name_plural = 'Pozycje zamówienia'

    def __str__(self):
        return f'{self.supply_item.name}: {self.quantity}'
