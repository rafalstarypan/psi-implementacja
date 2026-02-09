# apps/volunteers/serializers.py
from rest_framework import serializers
from .models import Schedule, Task
from django.core.exceptions import ValidationError as DjangoValidationError

class TaskSerializer(serializers.ModelSerializer):
    volunteers_count = serializers.SerializerMethodField()  # shows usernames

    class Meta:
        model = Task
        fields = [
            'task_id',
            'name',
            'description',
            'datetime',
            'duration_in_minutes',
            'maxVolunteers',
            'volunteers_count',
        ]

    def get_volunteers_count(self, obj):
        return obj.volunteers.count()


class ScheduleSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)  # uses related_name='tasks' from Task model

    class Meta:
        model = Schedule
        fields = [
            'schedule_id',
            'name',
            'start_date',
            'end_date',
            'tasks',
        ]


class TaskSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = []

    def create(self, validated_data):

        task = self.context['task']
        user = self.context['request'].user
        
        try:
            task.add_volunteer(user)
        except (ValueError, DjangoValidationError) as e:
            raise serializers.ValidationError({'detail': str(e)})

        return task



class TaskRemoveVolunteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = []

    def create(self, validated_data):
        task = self.context['task']
        user = self.context['request'].user

        try:
            task.remove_volunteer(user)
        except (ValueError, DjangoValidationError) as e:
            raise serializers.ValidationError({'detail': str(e)})

        return task

