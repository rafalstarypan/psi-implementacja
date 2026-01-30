"""
Admin configuration for animals app.
"""
from django.contrib import admin
from .models import Animal, BehavioralTag, Intake, Medication, Vaccination, MedicalProcedure


class MedicationInline(admin.TabularInline):
    model = Medication
    extra = 0
    readonly_fields = ['created_at']


class VaccinationInline(admin.TabularInline):
    model = Vaccination
    extra = 0
    readonly_fields = ['created_at']


class MedicalProcedureInline(admin.TabularInline):
    model = MedicalProcedure
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['animal_id', 'name', 'species', 'breed', 'sex', 'status', 'intake_date']
    list_filter = ['species', 'sex', 'status']
    search_fields = ['name', 'animal_id', 'breed', 'transponder_number']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MedicationInline, VaccinationInline, MedicalProcedureInline]

    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('animal_id', 'name', 'species', 'breed', 'birth_date', 'sex')
        }),
        ('Cechy fizyczne', {
            'fields': ('coat_color', 'weight', 'identifying_marks')
        }),
        ('Status i identyfikacja', {
            'fields': ('status', 'transponder_number', 'microchipping_date')
        }),
        ('Dodatkowe informacje', {
            'fields': ('notes', 'intake_date', 'created_at', 'updated_at')
        }),
    )


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['medication_name', 'animal', 'dosage', 'start_date', 'end_date', 'performed_by']
    list_filter = ['start_date', 'performed_by']
    search_fields = ['medication_name', 'animal__name', 'reason']
    readonly_fields = ['created_at']


@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ['vaccine_name', 'animal', 'vaccination_date', 'expiration_date', 'next_due_date', 'performed_by']
    list_filter = ['vaccination_date', 'performed_by']
    search_fields = ['vaccine_name', 'animal__name', 'vaccine_for']
    readonly_fields = ['created_at']


@admin.register(MedicalProcedure)
class MedicalProcedureAdmin(admin.ModelAdmin):
    list_display = ['description_short', 'animal', 'procedure_date', 'cost', 'performed_by']
    list_filter = ['procedure_date', 'performed_by']
    search_fields = ['description', 'animal__name']
    readonly_fields = ['created_at']

    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Opis'

@admin.register(Intake)
class IntakeAdmin(admin.ModelAdmin):
    list_display = ['animal', 'intake_type', 'intake_date']
    list_filter = ['intake_type', 'intake_date']
    search_fields = ['animal__name', 'notes']
    readonly_fields = ['created_at']

@admin.register(BehavioralTag)
class BehavioralTagAdmin(admin.ModelAdmin):
    list_display = ['behavioral_tag_name']
    list_filter = ['behavioral_tag_name']
    search_fields = ['behavioral_tag_name']
    readonly_fields = ['created_at']