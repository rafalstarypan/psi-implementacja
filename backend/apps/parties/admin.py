from django.contrib import admin
from .models import Address, Person, Institution

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    readonly_fields = ['created_at']

class PersonInline(admin.TabularInline):
    model = Person
    extra = 0
    readonly_fields = ['created_at']

class InstitutionInline(admin.TabularInline):
    model = Institution
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['person_id', 'firstname', 'lastname', 'phone_number', 'email_address']
    list_filter = ['firstname', 'lastname', 'phone_number', 'email_address']
    search_fields = ['firstname', 'lastname', 'phone_number', 'email_address']
    readonly_fields = ['person_id', 'created_at', 'updated_at']
    inlines = [AddressInline]

    fieldsets = (
        ('Basic informations', {
            'fields': ('person_id', 'firstname', 'lastname', 'phone_number', 'email_address')
        })
    )


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['institution_id', 'name', 'phone_number', 'email_address']
    list_filter = ['name', 'phone_number', 'email_address']
    search_fields = ['name', 'phone_number', 'email_address']
    readonly_fields = ['institution_id', 'created_at', 'updated_at']
    inlines = [AddressInline]

    fieldsets = (
        ('Basic informations', {
            'fields': ('institution_id', 'name', 'phone_number', 'email_address')
        })
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
        })
    )