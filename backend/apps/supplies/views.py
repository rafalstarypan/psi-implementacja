"""
Views for supplies app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from decimal import Decimal, InvalidOperation
from apps.accounts.permissions import IsEmployee
from .models import SupplyItem, SupplyCategory, Inventory, InventoryLog, InventoryOperationType
from .serializers import (
    SupplyItemListSerializer,
    SupplyItemDetailSerializer,
    SupplyCategorySerializer,
    InventoryLogSerializer,
)
from .filters import SupplyItemFilter


class SupplyItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing supply items.

    list: Get all supply items with optional filtering and search.
    retrieve: Get detailed information about a single supply item.
    """
    permission_classes = [IsEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SupplyItemFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category__name']
    ordering = ['name']

    def get_queryset(self):
        """
        Get queryset with optimized joins.
        """
        return SupplyItem.objects.select_related(
            'category', 'unit', 'inventory'
        ).all()

    def get_serializer_class(self):
        """
        Return different serializer for list and detail views.
        """
        if self.action == 'retrieve':
            return SupplyItemDetailSerializer
        return SupplyItemListSerializer

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """
        Get inventory logs for a specific supply item.
        """
        supply_item = self.get_object()
        try:
            logs = supply_item.inventory.logs.select_related('performed_by').all()
            page = self.paginate_queryset(logs)
            if page is not None:
                serializer = InventoryLogSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = InventoryLogSerializer(logs, many=True)
            return Response(serializer.data)
        except Inventory.DoesNotExist:
            return Response([])

    @action(detail=True, methods=['post'])
    def update_inventory(self, request, pk=None):
        """
        Update inventory for a supply item (inbound/outbound).
        """
        supply_item = self.get_object()
        change_type = request.data.get('change_type')
        quantity_change = request.data.get('quantity_change')
        reason = request.data.get('reason', '')

        if change_type not in ['in', 'out']:
            return Response(
                {'error': 'change_type must be "in" or "out"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity_change = Decimal(str(quantity_change))
            if quantity_change <= 0:
                raise ValueError()
        except (TypeError, ValueError, InvalidOperation):
            return Response(
                {'error': 'quantity_change must be a positive number'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Get or create inventory
            inventory, _ = Inventory.objects.get_or_create(supply_item=supply_item)

            # Calculate new quantity
            if change_type == 'in':
                inventory.current_quantity += quantity_change
                operation_type = InventoryOperationType.INBOUND
            else:
                if inventory.current_quantity < quantity_change:
                    return Response(
                        {'error': 'Insufficient stock'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                inventory.current_quantity -= quantity_change
                operation_type = InventoryOperationType.OUTBOUND

            inventory.save()

            # Create log entry
            InventoryLog.objects.create(
                inventory=inventory,
                operation_type=operation_type,
                quantity=quantity_change,
                comment=reason,
                performed_by=request.user,
            )

        return Response({'status': 'ok', 'new_quantity': inventory.current_quantity})


class SupplyCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing supply categories.
    """
    queryset = SupplyCategory.objects.all()
    serializer_class = SupplyCategorySerializer
    permission_classes = [IsEmployee]
    pagination_class = None
