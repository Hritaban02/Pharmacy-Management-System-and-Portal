from django.contrib import admin
from django.contrib.auth.models import Group
from phone_number.models import Staff_Phone, Vendor_Phone

from .models import Staff, Vendor

# Register your models here.
# admin.site.register(Customer)

admin.site.unregister(Group)


class VendorPhoneNumberInLine(admin.StackedInline):
    model = Vendor_Phone
    extra = 1
    max_num = 2


class StaffPhoneNumberInLine(admin.StackedInline):
    model = Staff_Phone
    extra = 1
    max_num = 2


class VendorAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'email', 'company_name']}),
        ('Address information',
         {'fields': ['street_number', 'street_name', 'building_number', 'city', 'state', 'country', 'zip']}),
    ]

    inlines = [VendorPhoneNumberInLine]


admin.site.register(Vendor, VendorAdmin)


class StaffAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'email', 'first_name', 'middle_name', 'last_name', 'date_of_birth']}),
        ('Address information',
         {'fields': ['street_number', 'street_name', 'apt_number', 'city', 'state', 'country', 'zip']}),
    ]

    inlines = [StaffPhoneNumberInLine]


admin.site.register(Staff, StaffAdmin)
