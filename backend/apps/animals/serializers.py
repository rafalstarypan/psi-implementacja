"""
Serializers for animals app.
"""
from datetime import date
from time import timezone
from rest_framework import serializers
from .models import Animal, BehavioralTag, Intake, Medication, Photo, Vaccination, MedicalProcedure
from apps.accounts.serializers import UserMinimalSerializer
import requests
from .services.intake_source_service import SourceService

class PhotoListSerializer(serializers.ModelSerializer):
    """Serializer for Animal Photo list view."""
    class Meta:
        model = Photo
        fields = [
            'filename', 
            'is_identification_photo', 'url'
        ]
        read_only_fields = ['url']   

class PhotoDetailSerializer(serializers.ModelSerializer):
    """Serializer for Animal Photo detail view."""
    class Meta:
        model = Photo
        fields = [
            'photo_id',
            'filename', 
            'url',
            'is_identification_photo',
            'upload_date',
        ]
        

class PhotoCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = [
            'is_identification_photo',
            'filename',
            'url',
            'upload_date'
        ]
        read_only_fields = ['url', 'upload_date']

    def create(self, validated_data):
        validated_data['url'] = f"/media/animals/{validated_data['filename']}"
        photo = Photo.objects.create(**validated_data)
        return photo



class IntakeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Intake
        fields = [
            'intake_id',
            'intake_date', 
            'intake_type', 
            'animal_condition', 
            'location', 
            'notes'
        ]


class IntakeCreateSerializer(serializers.ModelSerializer):

    source = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = Intake
        fields = [
            'intake_id',
            'intake_type', 
            'intake_date',
            'animal_condition', 
            'location', 
            'notes',
            'source_type',
            'source'
        ]
        read_only_fields = ['intake_id', 'intake_date']

    def create(self, validated_data):

        source_data = validated_data.pop("source", None)
        source_type = validated_data.get("source_type")

        if source_data and source_type:
            if set(source_data.keys()) == {"id"}:
                if SourceService.exists(source_type, source_data["id"], context=self.context):
                    validated_data["source_id"] = source_data["id"]
                else:
                    validated_data["source_id"] = None
                    validated_data["source_type"] = None
            else:
                validated_data["source_id"] = SourceService.create(
                    source_type, source_data["data"], context=self.context
                )
        return Intake.objects.create(**validated_data)



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

class IntakeListSerializer(serializers.ModelSerializer):


    class Meta:
        model = Intake
        fields = [
            'intake_date', 
            'intake_type', 
            'animal_condition', 
            'location',
            'source_type',
            'source_id'
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

    behavioral_tags = serializers.SlugRelatedField(
        many=True,
        slug_field="behavioral_tag_name",
        queryset=BehavioralTag.objects.all(),
        required=False,
    )

    parents = serializers.SlugRelatedField(
        many=True,
        slug_field="animal_id",      
        queryset=Animal.objects.all(),      
        required=False,         
    )

    photos = PhotoListSerializer(many=True, read_only=True)

    intakes = IntakeListSerializer(many=True, read_only=True)

    class Meta:
        model = Animal
        fields = [
            'id', 'animal_id', 'name', 'species', 'species_display',
            'breed', 'birth_date', 'age_display', 'sex', 'sex_display',
            'coat_color', 'weight', 'identifying_marks', 'transponder_number',
            'status', 'status_display', 'notes', 'intake_date', 'microchipping_date',
            'medications', 'vaccinations', 'medical_procedures', 'behavioral_tags', 'parents', 'photos', 'intakes', 'last_measured'
        ]

    def get_medications(self, obj):
        """Get medications with is_active status."""
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


class AnimalCreateSerializer(serializers.ModelSerializer):

    behavioral_tags = serializers.SlugRelatedField(
        many=True,
        slug_field="behavioral_tag_name",
        queryset=BehavioralTag.objects.all(),
        required=False,
        error_messages={
        "does_not_exist": "Behavioral tag '{value}' does not exist."
    }
    )

    parents = serializers.SlugRelatedField(
        many=True,
        slug_field="animal_id",      
        queryset=Animal.objects.all(),
        required=False,
        error_messages={
        "does_not_exist": "Animal with animal_id '{value}' does not exist."
        }
    )

    photos = PhotoCreateSerializer(many=True, required=False)

    intakes = IntakeCreateSerializer(required=True, write_only=True)

    class Meta:
        model = Animal
        fields = [
            'animal_id', 'name', 'species',
            'breed', 'birth_date', 'sex',
            'coat_color', 'weight', 'identifying_marks', 'transponder_number',
            'status', 'notes', 'microchipping_date', 'last_measured',
            'behavioral_tags','parents','photos', 'intakes'
        ]
        read_only_fields = ['animal_id', 'last_measured']

    def create(self, validated_data):
    
        parents = validated_data.pop('parents', [])
        tags = validated_data.pop('behavioral_tags', [])
        photos_data = validated_data.pop('photos', [])
        intake_data = validated_data.pop('intakes', None)

        validated_data['last_measured'] = date.today()
        animal = Animal.objects.create(
            **validated_data
        )
        if intake_data:
            intake_serializer = IntakeCreateSerializer(
                data=intake_data,
                context=self.context
            )
            intake_serializer.is_valid(raise_exception=True)
            intake_serializer.save(animal=animal)
        if photos_data:
            for photo_data in photos_data:
                Photo.objects.create(animal=animal, **photo_data)
        if parents:
            animal.parents.set(parents)
        if tags:
            animal.behavioral_tags.set(tags)
        return animal
    
    def validate_parents(self, value):
        if len(value) > 2:
            raise serializers.ValidationError("An animal can have at most 2 parents.")
        return value


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



class BehavioralTagListSerializer(serializers.ModelSerializer):

    class Meta:
        model = BehavioralTag
        fields = [
            'behavioral_tag_name', 
        ]

class BehavioralTagDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = BehavioralTag
        fields = [
            'behavioral_tag_name', 
            'description',
        ]


from .models import Animal

class AnimalUpdateSerializer(serializers.ModelSerializer):
    # Input: accept list of animal_id strings
    parents = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        write_only=True  # only used for input
    )

    # Output: show list of animal_id strings
    parents_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Animal
        fields = [
            "name",
            "species",
            "breed",
            "sex",
            "birth_date",
            "coat_color",
            "weight",
            "last_measured",
            "identifying_marks",
            "transponder_number",
            "microchipping_date",
            "behavioral_tags",
            "parents",
            "parents_display",
            "status",
        ]
        extra_kwargs = {
            field: {"required": False, "allow_null": True}
            for field in fields
        }

    def get_parents_display(self, obj):
        # Return list of animal_id strings for frontend
        return [p.animal_id for p in obj.parents.all()]

    def validate_parents(self, value):
        """Convert list of animal_id strings to actual Animal objects"""
        if value is None:
            return []

        animals = list(Animal.objects.filter(animal_id__in=value))

        if len(animals) != len(value):
            found_ids = {a.animal_id for a in animals}
            missing = [aid for aid in value if aid not in found_ids]
            raise serializers.ValidationError(f"Parents not found: {missing}")

        return animals

    def update(self, instance, validated_data):
        # Pop ManyToMany fields first
        parents = validated_data.pop("parents", None)
        behavioral_tags = validated_data.pop("behavioral_tags", None)

        # Update normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update M2M fields properly
        if parents is not None:
            instance.parents.set(parents)
        if behavioral_tags is not None:
            instance.behavioral_tags.set(behavioral_tags)

        return instance

