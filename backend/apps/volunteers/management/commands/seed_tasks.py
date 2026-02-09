import uuid
from django.core.management.base import BaseCommand
from apps.volunteers.models import Schedule, Task, TaskStatus
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seed initial schedules and tasks data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting seeding schedules and tasks...'))
        self.seed_schedules()
        self.seed_tasks()
        self.stdout.write(self.style.SUCCESS('Seeding schedules and tasks completed!'))


    def seed_schedules(self):
        schedules_data = [
            {
                'name': 'Weekend Morning Shift',
                'start_date': timezone.now().date(),
                'end_date': (timezone.now() + timedelta(days=30)).date(),
            },
            {
                'name': 'Weekday Afternoon Shift',
                'start_date': timezone.now().date(),
                'end_date': (timezone.now() + timedelta(days=30)).date(),
            },
        ]

        for data in schedules_data:
            schedule, created = Schedule.objects.get_or_create(
                name=data['name'],
                defaults={
                    'start_date': data['start_date'],
                    'end_date': data['end_date'],
                    'schedule_id': uuid.uuid4()
                }
            )
            if created:
                self.stdout.write(f'Created schedule: {schedule.name}')
            else:
                self.stdout.write(self.style.WARNING(f'Schedule already exists: {schedule.name}'))


    def seed_tasks(self):
        # Make sure schedules exist
        schedules = Schedule.objects.all()
        if not schedules.exists():
            self.stdout.write(self.style.ERROR('No schedules found. Run schedule seeding first.'))
            return

        tasks_data = [
            {
                'name': 'Clean animal cages',
                'description': 'Cleaning and sanitizing all animal cages.',
                'datetime_offset_days': 1,
                'duration_in_minutes': 60,
                'maxVolunteers': 3,
                'schedule': schedules.first(), 
                'status': TaskStatus.AVAILABLE,
            },
            {
                'name': 'Feed animals',
                'description': 'Feed animals according to their dietary plan.',
                'datetime_offset_days': 2,
                'duration_in_minutes': 45,
                'maxVolunteers': 2,
                'schedule': schedules.last(), 
                'status': TaskStatus.COMPLETED, 
            },
            {
                'name': 'Socialize dogs',
                'description': 'Play with dogs to keep them happy and healthy.',
                'datetime_offset_days': 3,
                'duration_in_minutes': 30,
                'maxVolunteers': 4,
                'schedule': schedules.first(),
                'status': TaskStatus.AVAILABLE,
            },
                        {
                'name': 'Socialize cats',
                'description': 'Play with dogs to keep them happy and healthy.',
                'datetime_offset_days': 1,
                'duration_in_minutes': 30,
                'maxVolunteers': 1,
                'schedule': schedules.first(),
                'status': TaskStatus.AVAILABLE,
            },
        ]

        for data in tasks_data:
            task_datetime = timezone.now() + timedelta(days=data.pop('datetime_offset_days'))
            task, created = Task.objects.get_or_create(
                name=data['name'],
                schedule=data['schedule'],
                defaults={
                    'description': data['description'],
                    'datetime': task_datetime,
                    'duration_in_minutes': data['duration_in_minutes'],
                    'maxVolunteers': data['maxVolunteers'],
                    'status': data['status'],
                    'task_id': uuid.uuid4()
                }
            )
            if created:
                self.stdout.write(f'Created task: {task.name}')
            else:
                self.stdout.write(self.style.WARNING(f'Task already exists: {task.name}'))
