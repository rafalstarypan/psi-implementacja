from django.contrib import admin
from .models import Address, Person, Institution




@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['person_id', 'firstname', 'lastname', 'phone_number', 'email_address', 'address']
    list_filter = ['firstname', 'lastname', 'phone_number', 'email_address']
    search_fields = ['firstname', 'lastname', 'phone_number', 'email_address']
    readonly_fields = ['person_id', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic informations', {
            'fields': ('person_id', 'firstname', 'lastname', 'phone_number', 'email_address')
        }),
    )


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['institution_id', 'name', 'phone_number', 'email_address', 'address']
    list_filter = ['name', 'phone_number', 'email_address']
    search_fields = ['name', 'phone_number', 'email_address']
    readonly_fields = ['institution_id', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic informations', {
            'fields': ('institution_id', 'name', 'phone_number', 'email_address')
        }),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['street', 'city', 'postal_code']
    list_filter = ['city', 'street', 'postal_code']
    search_fields = ['street', 'city', 'postal_code']
    readonly_fields = ['address_id', 'created_at', 'updated_at']

    fieldsets = (
        ('Address details', {
            'fields': ('address_id', 'street', 'city', 'postal_code', 'building_number', 'apartment_number')
        }),
    )