from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ModelMultipleChoiceField
from apps.accounts.models import User
from .models import Schedule, Task

class TaskAdminForm(ModelForm):
    volunteers = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Task
        fields = '__all__'

    def clean_volunteers(self):
        """Ensure the number of volunteers does not exceed maxVolunteers."""
        volunteers = self.cleaned_data.get('volunteers')
        max_vols = self.cleaned_data.get('maxVolunteers')
        if volunteers and max_vols is not None and len(volunteers) > max_vols:
            raise ValidationError(f"Cannot assign more than {max_vols} volunteers to this task.")
        return volunteers
    

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = ('name', 'datetime', 'schedule', 'maxVolunteers', 'volunteer_count', 'is_full')
    list_filter = ('schedule',)
    search_fields = ('name', 'description')
    filter_horizontal = ('volunteers',) 

    def volunteer_count(self, obj):
        return obj.volunteers.count()
    volunteer_count.short_description = "Current Volunteers"

    def is_full(self, obj):
        return obj.is_full()
    is_full.boolean = True
    is_full.short_description = "Task Full"   


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)