from django.urls import path, include
from apps.volunteers.views import ScheduleViewSet, TaskViewSet
from rest_framework.routers import DefaultRouter


app_name = 'volunteers'

router = DefaultRouter()
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'tasks', TaskViewSet, basename='task')


urlpatterns = [
    path('', include(router.urls)),
]
