"""
URL configuration for supplies app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplyItemViewSet, SupplyCategoryViewSet

app_name = 'supplies'

router = DefaultRouter()
router.register(r'items', SupplyItemViewSet, basename='supply-item')
router.register(r'categories', SupplyCategoryViewSet, basename='supply-category')

urlpatterns = [
    path('', include(router.urls)),
]
