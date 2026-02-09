import uuid
from django.db import models
from django.core.exceptions import ValidationError

from apps.accounts.models import User

class TaskStatus(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    PERSON_LIMIT_REACHED = 'PERSON_LIMIT_REACHED', 'Person Limit Reached'
    COMPLETED = 'COMPLETED', 'Completed'
    UNCOMPLETED = 'UNCOMPLETED', 'Uncompleted'


class Schedule(models.Model):
    """ Work schedule for volunteers. """
    schedule_id = models.CharField(
        verbose_name='Address Identifier',
        max_length=50,
        unique=True,
        default=uuid.uuid4,  
        editable=False,
    )
    name = models.CharField(
        verbose_name='Schedule Name',
        max_length=50,
    )

    start_date = models.DateField(
        verbose_name='Start Date',
        null=False,
        blank=False,
    )

    end_date = models.DateField(
        verbose_name='End Date',
        null=False,
        blank=False,
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        ordering = ['-start_date', '-end_date']

    def __str__(self):
        return f'{self.name} {self.start_date} - {self.end_date}'



class Task(models.Model):
    """ Task for volunteers. """
    task_id = models.CharField(
        verbose_name='Task Identifier',
        max_length=50,
        unique=True,
        default=uuid.uuid4,  
        editable=False,
    )
    name = models.CharField(
        verbose_name='Task Name',
        max_length=50,
    )

    description = models.TextField(
        verbose_name='Task Description',
        null=True,
        blank=True,
    )

    datetime = models.DateTimeField(
        verbose_name='Task Date and Time',
        null=False,
        blank=False,
    )

    duration_in_minutes = models.PositiveIntegerField(
        verbose_name='Task Duration in Minutes',
        null=False,
        blank=False,
    )

    maxVolunteers = models.PositiveIntegerField(
        verbose_name='Maximum Volunteers',
        null=False,
        blank=False,
    )

    schedule = models.ForeignKey(
        Schedule,
        verbose_name='Schedule',
        on_delete=models.CASCADE,
        related_name='tasks',
    )

    volunteers = models.ManyToManyField(
        User,
        verbose_name='Volunteers',
        blank=True,
        related_name='tasks_signed_up',
    )

    status = models.CharField(
        verbose_name='Task Status',
        max_length=20,
        choices=TaskStatus.choices
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-datetime']

    def __str__(self):
        return f'{self.name} {self.datetime}'
    

    def add_volunteer(self, user):
        if self.status == TaskStatus.COMPLETED or self.status == TaskStatus.UNCOMPLETED:
            raise ValidationError("Cannot add volunteer to a closed task.")
        if self.volunteers.filter(pk=user.pk).exists():
            raise ValueError("User is already signed up for this task.")
        if self.volunteers.count() >= self.maxVolunteers:
            raise ValueError("Task is already full!")
        self.volunteers.add(user)
        if self.is_full():
            self.status = TaskStatus.PERSON_LIMIT_REACHED
            self.save(update_fields=['status'])

    def remove_volunteer(self, user: User):
        if self.status == TaskStatus.COMPLETED or self.status == TaskStatus.UNCOMPLETED:
            raise ValidationError("Cannot remove volunteer from a closed task.")
        if user in self.volunteers.all():
            if self.is_full():
                self.status = TaskStatus.AVAILABLE
                self.save(update_fields=['status'])
            self.volunteers.remove(user)
        else:
            raise ValidationError("User is not signed up for this task.")

    def is_full(self) -> bool:
        """Check if the task has reached max volunteers."""
        return self.volunteers.count() >= self.maxVolunteers

