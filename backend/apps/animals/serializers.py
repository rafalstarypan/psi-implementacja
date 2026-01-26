"""
Serializers for animals app.
"""
from rest_framework import serializers
from .models import Animal, Medication, Vaccination, MedicalProcedure
from apps.accounts.serializers import UserMinimalSerializer


class AnimalListSerializer(serializers.ModelSerializer):
    """Serializer for Animal list view."""
    species_display = serializers.CharField(source='get_species_display', read_only=True)
    sex_display = serializers.CharField(source='get_sex_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    age_display = serializers.CharField(read_only=True)

    class Meta:
        model = Animal
        fields = [
            'id', 'animal_id', 'name', 'species', 'species_display',
            'breed', 'birth_date', 'age_display', 'sex', 'sex_display',
            'status', 'status_display', 'intake_date'
        ]


class AnimalDetailSerializer(serializers.ModelSerializer):
    """Serializer for Animal detail view."""
    species_display = serializers.CharField(source='get_species_display', read_only=True)
    sex_display = serializers.CharField(source='get_sex_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    age_display = serializers.CharField(read_only=True)
    medications = serializers.SerializerMethodField()
    vaccinations = serializers.SerializerMethodField()
    medical_procedures = serializers.SerializerMethodField()

    class Meta:
        model = Animal
        fields = [
            'id', 'animal_id', 'name', 'species', 'species_display',
            'breed', 'birth_date', 'age_display', 'sex', 'sex_display',
            'coat_color', 'weight', 'identifying_marks', 'transponder_number',
            'status', 'status_display', 'notes', 'intake_date', 'microchipping_date',
            'medications', 'vaccinations', 'medical_procedures'
        ]

    def get_medications(self, obj):
        """Get medications with is_active status."""
        from datetime import date
        medications = obj.medications.select_related('performed_by').all()
        result = []
        for med in medications:
            is_active = med.end_date is None or med.end_date >= date.today()
            result.append({
                'id': med.id,
                'medication_name': med.medication_name,
                'dosage': med.dosage,
                'frequency': med.frequency,
                'start_date': med.start_date,
                'end_date': med.end_date,
                'notes': med.notes,
                'is_active': is_active,
                'prescribed_by_name': med.performed_by.full_name if med.performed_by else '-',
            })
        return result

    def get_vaccinations(self, obj):
        """Get vaccinations."""
        vaccinations = obj.vaccinations.select_related('performed_by').all()
        return [
            {
                'id': vac.id,
                'vaccine_name': vac.vaccine_name,
                'vaccination_date': vac.vaccination_date,
                'next_due_date': vac.next_due_date,
                'batch_number': vac.vaccine_batch_number,
                'notes': '',
                'administered_by_name': vac.performed_by.full_name if vac.performed_by else '-',
            }
            for vac in vaccinations
        ]

    def get_medical_procedures(self, obj):
        """Get medical procedures."""
        procedures = obj.procedures.select_related('performed_by').all()
        return [
            {
                'id': proc.id,
                'procedure_name': proc.description[:50],
                'procedure_date': proc.procedure_date,
                'description': proc.description,
                'outcome': proc.result,
                'follow_up_required': False,
                'follow_up_date': None,
                'performed_by_name': proc.performed_by.full_name if proc.performed_by else '-',
            }
            for proc in procedures
        ]


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for Medication."""
    performed_by = UserMinimalSerializer(read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)

    class Meta:
        model = Medication
        fields = [
            'id', 'animal', 'medication_name', 'dosage', 'frequency',
            'start_date', 'end_date', 'reason', 'notes',
            'performed_by', 'performed_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'animal']


class MedicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Medication."""

    class Meta:
        model = Medication
        fields = [
            'medication_name', 'dosage', 'frequency',
            'start_date', 'end_date', 'reason', 'notes', 'performed_by'
        ]

    def create(self, validated_data):
        animal = self.context['animal']
        validated_data['animal'] = animal
        if 'performed_by' not in validated_data:
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                validated_data['performed_by'] = request.user
        return super().create(validated_data)


class VaccinationSerializer(serializers.ModelSerializer):
    """Serializer for Vaccination."""
    performed_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Vaccination
        fields = [
            'id', 'animal', 'vaccine_name', 'vaccine_for', 'vaccine_batch_number',
            'vaccination_date', 'expiration_date', 'next_due_date',
            'performed_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VaccinationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Vaccination."""

    class Meta:
        model = Vaccination
        fields = [
            'vaccine_name', 'vaccine_for', 'vaccine_batch_number',
            'vaccination_date', 'expiration_date', 'next_due_date', 'performed_by'
        ]

    def create(self, validated_data):
        animal = self.context['animal']
        validated_data['animal'] = animal
        if 'performed_by' not in validated_data:
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                validated_data['performed_by'] = request.user
        return super().create(validated_data)


class MedicalProcedureSerializer(serializers.ModelSerializer):
    """Serializer for MedicalProcedure."""
    performed_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = MedicalProcedure
        fields = [
            'id', 'animal', 'procedure_date', 'description', 'result',
            'cost', 'notes', 'performed_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MedicalProcedureCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating MedicalProcedure."""

    class Meta:
        model = MedicalProcedure
        fields = [
            'procedure_date', 'description', 'result',
            'cost', 'notes', 'performed_by'
        ]

    def create(self, validated_data):
        animal = self.context['animal']
        validated_data['animal'] = animal
        if 'performed_by' not in validated_data:
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                validated_data['performed_by'] = request.user
        return super().create(validated_data)


class VeterinarianSerializer(serializers.ModelSerializer):
    """Serializer for listing veterinarians (employees)."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        from apps.accounts.models import User
        model = User
        fields = ['id', 'full_name', 'email']
