"""
Admin configuration for supplies app.
"""
from django.contrib import admin
from .models import (
    SupplyCategory, UnitOfMeasure, Supplier, SupplyItem,
    Inventory, InventoryLog, SupplyOrder, SupplyOrderLine
)


@admin.register(SupplyCategory)
class SupplyCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']
    search_fields = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'email']
    search_fields = ['name']


class InventoryInline(admin.StackedInline):
    model = Inventory
    can_delete = False


@admin.register(SupplyItem)
class SupplyItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'min_stock', 'get_current_quantity', 'get_stock_status']
    list_filter = ['category']
    search_fields = ['name', 'description']
    inlines = [InventoryInline]

    def get_current_quantity(self, obj):
        return obj.current_quantity
    get_current_quantity.short_description = 'Aktualna ilość'

    def get_stock_status(self, obj):
        status_map = {
            'low': 'Niski',
            'warning': 'Uwaga',
            'good': 'Dobry'
        }
        return status_map.get(obj.stock_status, obj.stock_status)
    get_stock_status.short_description = 'Status'


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['supply_item', 'current_quantity', 'expiration_date']
    search_fields = ['supply_item__name']


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ['inventory', 'operation_type', 'quantity', 'timestamp', 'performed_by']
    list_filter = ['operation_type', 'timestamp']
    search_fields = ['inventory__supply_item__name', 'comment']
    readonly_fields = ['timestamp']


class SupplyOrderLineInline(admin.TabularInline):
    model = SupplyOrderLine
    extra = 1


@admin.register(SupplyOrder)
class SupplyOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'expected_delivery_date', 'status', 'issue_date']
    list_filter = ['status', 'supplier']
    search_fields = ['supplier__name']
    inlines = [SupplyOrderLineInline]
