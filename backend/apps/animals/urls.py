"""
URL configuration for animals app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnimalViewSet, VeterinarianListView, IntakeViewSet, BehavioralTagViewSet, PhotoViewSet


router = DefaultRouter()
router.register(r'animals/intakes', IntakeViewSet, basename='intake')
router.register(r'animals/behavioral-tags', BehavioralTagViewSet, basename='behavioral-tag')
router.register(r'animals/photos', PhotoViewSet, basename='photo')
router.register(r'animals', AnimalViewSet, basename='animal')


urlpatterns = [
    path('veterinarians/', VeterinarianListView.as_view(), name='veterinarian-list'),
    path('', include(router.urls)),
]
