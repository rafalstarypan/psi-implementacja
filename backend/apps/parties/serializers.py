from rest_framework import serializers
from .models import Address, Person, Institution



class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = [
            'address_id',
            'city',
            'postal_code',
            'street',
            'building_number',
            'apartment_number'
        ]

class AddressCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Address."""

    class Meta:
        model = Address
        fields = [
            'city',
            'postal_code',
            'street',
            'building_number',
            'apartment_number',
        ]


class PersonListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = [
            'email_address',
            'firstname',
            'lastname'
        ]


class PersonDetailSerializer(serializers.ModelSerializer):

    address = AddressSerializer(read_only=True)

    class Meta:
        model = Person
        fields = [
            'person_id',
            'phone_number',
            'email_address',
            'firstname',
            'lastname',
            'address'
        ]


class PersonCreateSerializer(serializers.ModelSerializer):
    address = AddressCreateSerializer()

    class Meta:
        model = Person
        fields = [
            'phone_number',
            'email_address',
            'firstname',
            'lastname',
            'address'
        ]

    def create(self, validated_data):

        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        person = Person.objects.create(
            address=address,
            **validated_data
        )

        return person

class InstitutionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Institution
        fields = [
            'email_address',
            'name'
        ]

class InstitutionDetailSerializer(serializers.ModelSerializer):

    address = AddressSerializer(read_only=True)

    class Meta:
        model = Institution
        fields = [
            'institution_id',
            'phone_number',
            'email_address',
            'name',
            'address'
        ]


class InstitutionCreateSerializer(serializers.ModelSerializer):
    address = AddressCreateSerializer()

    class Meta:
        model = Institution
        fields = [
            'institution_id',
            'phone_number',
            'email_address',
            'name',
            'address'
        ]

    def create(self, validated_data):

        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        institution = Institution.objects.create(
            address=address,
            **validated_data
        )
        return institution