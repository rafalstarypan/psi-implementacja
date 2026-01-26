"""
Serializers for supplies app.
"""
from rest_framework import serializers
from .models import (
    SupplyCategory, UnitOfMeasure, Supplier, SupplyItem,
    Inventory, InventoryLog, SupplyOrder, SupplyOrderLine,
    SupplyOrderStatus
)
from apps.accounts.serializers import UserMinimalSerializer


class SupplyCategorySerializer(serializers.ModelSerializer):
    """Serializer for SupplyCategory."""

    class Meta:
        model = SupplyCategory
        fields = ['id', 'name']


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    """Serializer for UnitOfMeasure."""

    class Meta:
        model = UnitOfMeasure
        fields = ['id', 'name', 'abbreviation']


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier."""

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'phone_number', 'email']


class InventoryLogSerializer(serializers.ModelSerializer):
    """Serializer for InventoryLog."""
    performed_by = UserMinimalSerializer(read_only=True)
    operation_type_display = serializers.CharField(
        source='get_operation_type_display',
        read_only=True
    )

    class Meta:
        model = InventoryLog
        fields = [
            'id', 'operation_type', 'operation_type_display',
            'quantity', 'comment', 'timestamp', 'performed_by'
        ]


class SupplyOrderLineSerializer(serializers.ModelSerializer):
    """Serializer for SupplyOrderLine."""
    supply_item_name = serializers.CharField(source='supply_item.name', read_only=True)

    class Meta:
        model = SupplyOrderLine
        fields = ['id', 'supply_item', 'supply_item_name', 'quantity']


class SupplyOrderSerializer(serializers.ModelSerializer):
    """Serializer for SupplyOrder."""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    lines = SupplyOrderLineSerializer(many=True, read_only=True)

    class Meta:
        model = SupplyOrder
        fields = [
            'id', 'supplier', 'supplier_name', 'issue_date',
            'expected_delivery_date', 'status', 'status_display',
            'notes', 'lines'
        ]


class SupplyOrderMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for SupplyOrder (for list views)."""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = SupplyOrder
        fields = [
            'id', 'supplier_name', 'expected_delivery_date',
            'status', 'status_display', 'quantity'
        ]

    def get_quantity(self, obj):
        """Get total quantity from order lines for specific supply item."""
        supply_item_id = self.context.get('supply_item_id')
        if supply_item_id:
            line = obj.lines.filter(supply_item_id=supply_item_id).first()
            return line.quantity if line else None
        return None


class InventorySerializer(serializers.ModelSerializer):
    """Serializer for Inventory."""

    class Meta:
        model = Inventory
        fields = ['current_quantity', 'expiration_date']


class SupplyItemListSerializer(serializers.ModelSerializer):
    """Serializer for SupplyItem list view."""
    category = SupplyCategorySerializer(read_only=True)
    unit = UnitOfMeasureSerializer(read_only=True)
    current_quantity = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    stock_status = serializers.CharField(read_only=True)
    next_delivery = serializers.SerializerMethodField()

    class Meta:
        model = SupplyItem
        fields = [
            'id', 'name', 'description', 'min_stock',
            'category', 'unit', 'current_quantity',
            'stock_status', 'next_delivery'
        ]

    def get_next_delivery(self, obj):
        """Get the next pending delivery for this item."""
        pending_order_line = SupplyOrderLine.objects.filter(
            supply_item=obj,
            order__status=SupplyOrderStatus.IN_PROGRESS
        ).select_related('order', 'order__supplier').order_by(
            'order__expected_delivery_date'
        ).first()

        if pending_order_line:
            return {
                'expected_date': pending_order_line.order.expected_delivery_date,
                'supplier_name': pending_order_line.order.supplier.name,
                'quantity': pending_order_line.quantity,
            }
        return None


class SupplyItemDetailSerializer(serializers.ModelSerializer):
    """Serializer for SupplyItem detail view."""
    category = SupplyCategorySerializer(read_only=True)
    unit = UnitOfMeasureSerializer(read_only=True)
    current_quantity = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    stock_status = serializers.CharField(read_only=True)
    pending_orders = serializers.SerializerMethodField()
    recent_logs = serializers.SerializerMethodField()

    class Meta:
        model = SupplyItem
        fields = [
            'id', 'name', 'description', 'min_stock',
            'category', 'unit', 'current_quantity',
            'stock_status', 'pending_orders', 'recent_logs'
        ]

    def get_pending_orders(self, obj):
        """Get pending orders for this supply item."""
        pending_lines = SupplyOrderLine.objects.filter(
            supply_item=obj,
            order__status=SupplyOrderStatus.IN_PROGRESS
        ).select_related('order', 'order__supplier').order_by(
            'order__expected_delivery_date'
        )

        return [
            {
                'id': line.order.id,
                'expected_delivery_date': line.order.expected_delivery_date,
                'supplier_name': line.order.supplier.name,
                'quantity': line.quantity,
                'status': line.order.status,
                'status_display': line.order.get_status_display(),
            }
            for line in pending_lines
        ]

    def get_recent_logs(self, obj):
        """Get recent inventory logs for this supply item."""
        try:
            logs = obj.inventory.logs.select_related('performed_by')[:20]
            return InventoryLogSerializer(logs, many=True).data
        except Inventory.DoesNotExist:
            return []
