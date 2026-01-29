"""
URL configuration for shelter_project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.core.urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/animals/', include('apps.animals.urls')),
    path('api/supplies/', include('apps.supplies.urls')),
    path('api/parties/', include('apps.parties.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
