from accounts.models import Customer, Staff, Vendor
from django.core.validators import RegexValidator
from django.db import models

phone_number_validator = RegexValidator(r'^[0-9]{10}$', 'The phone number should be of the form NNNNNNNNNN.')


# Create your models here.
class Customer_Phone(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, validators=[phone_number_validator], verbose_name='Phone Number',
                                    help_text='Enter a valid 10-digit phone number.')

    class Meta:
        unique_together = (("customer", "phone_number"),)


class Staff_Phone(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, validators=[phone_number_validator],
                                    verbose_name='Phone Number', help_text='Enter a valid 10-digit phone number.')

    class Meta:
        unique_together = (("staff", "phone_number"),)


class Vendor_Phone(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, validators=[phone_number_validator],
                                    verbose_name='Phone Number', help_text='Enter a valid 10-digit phone number.')

    class Meta:
        unique_together = (("vendor", "phone_number"),)
