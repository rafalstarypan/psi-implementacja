"""
URL configuration for animals app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnimalViewSet, VeterinarianListView

app_name = 'animals'

router = DefaultRouter()
router.register(r'', AnimalViewSet, basename='animal')

urlpatterns = [
    path('veterinarians/', VeterinarianListView.as_view(), name='veterinarian-list'),
    path('', include(router.urls)),
]
