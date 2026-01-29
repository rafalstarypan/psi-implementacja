"""
URL configuration for parties app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  PersonViewSet, InstitutionViewSet

app_name = 'parties'

router = DefaultRouter()
router.register(r'persons', PersonViewSet, basename='person')
router.register(r'institutions', InstitutionViewSet, basename='institution')

urlpatterns = [
    path('', include(router.urls)),
]
