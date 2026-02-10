"""
URL configuration for animals app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnimalViewSet, VeterinarianListView, IntakeViewSet, BehavioralTagViewSet, PhotoViewSet
from rest_framework_nested import routers


router = DefaultRouter()
router.register(r'animals', AnimalViewSet, basename='animal')

animals_router = routers.NestedDefaultRouter(router, r'animals', lookup='animal')
animals_router.register(r'intakes', IntakeViewSet, basename='animal-intakes')
animals_router.register(r'photos', PhotoViewSet, basename='animal-photos')
animals_router.register(r'behavioral-tags', BehavioralTagViewSet, basename='animal-behavioral-tags')

urlpatterns = [
    path('veterinarians/', VeterinarianListView.as_view(), name='veterinarian-list'),
    path('', include(router.urls)),
    path('', include(animals_router.urls)),
]
