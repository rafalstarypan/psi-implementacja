"""
Filters for supplies app.
"""
import django_filters
from .models import SupplyItem


class SupplyItemFilter(django_filters.FilterSet):
    """Filter for SupplyItem."""
    category = django_filters.NumberFilter(field_name='category__id')
    category_name = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains'
    )
    stock_status = django_filters.ChoiceFilter(
        method='filter_by_stock_status',
        choices=[
            ('low', 'Niski'),
            ('warning', 'Uwaga'),
            ('good', 'Dobry'),
        ]
    )

    class Meta:
        model = SupplyItem
        fields = ['category', 'category_name', 'stock_status']

    def filter_by_stock_status(self, queryset, name, value):
        """
        Filter supply items by their stock status.
        """
        items_with_status = []
        for item in queryset:
            if item.stock_status == value:
                items_with_status.append(item.id)
        return queryset.filter(id__in=items_with_status)
