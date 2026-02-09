from django.shortcuts import render
from apps.accounts.permissions import IsEmployeeOrVolunteer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.accounts import permissions
from rest_framework import viewsets
from .models import Schedule, Task
from .serializers import ScheduleSerializer, TaskRemoveVolunteerSerializer, TaskSerializer, TaskSignUpSerializer
from rest_framework.response import Response

permission_classes = [IsEmployeeOrVolunteer]
class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.prefetch_related('tasks__volunteers').all()
    serializer_class = ScheduleSerializer



permission_classes = [IsEmployeeOrVolunteer]
class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.objects.prefetch_related('volunteers').all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='signup')
    def signup(self, request, pk=None):
        task = self.get_object()
        serializer = TaskSignUpSerializer(data=request.data, context={'request': request, 'task': task})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'User signed up successfully',
            'volunteers_count': task.volunteers.count()
        })
    
    @action(detail=True, methods=['post'], url_path='remove')
    def remove(self, request, pk=None):
        task = self.get_object()
        serializer = TaskRemoveVolunteerSerializer(data=request.data, context={'request': request, 'task': task})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'User removed successfully',
            'volunteers_count': task.volunteers.count()
        })