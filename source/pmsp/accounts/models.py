from datetime import date

from django.contrib.auth.models import User
from django.core.validators import ValidationError, RegexValidator
from django.db import models
from django_countries.fields import CountryField

alphabet_validator = RegexValidator(r'^[a-zA-Z ]*$', 'Only alphabet characters are allowed.')
zip_code_validator = RegexValidator(r'^[0-9]{6}$', 'The zip code should be of the form DDDDDD.')


def adult_validator(date_value):
    age = (date.today() - date_value).days / 365
    if age < 18:
        raise ValidationError('You must be at least 18 years old.')


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Customer")
    email = models.EmailField(unique=True, help_text='Enter a valid email address.')
    first_name = models.CharField(max_length=200, validators=[alphabet_validator], verbose_name='First Name',
                                  help_text='Please enter only alphabets.')
    middle_name = models.CharField(max_length=200, blank=True, null=True, validators=[alphabet_validator],
                                   verbose_name='Middle Name',
                                   help_text='This field is optional. Please enter only alphabets.')
    last_name = models.CharField(max_length=200, validators=[alphabet_validator], verbose_name='Last Name',
                                 help_text='Please enter only alphabets.')
    date_of_birth = models.DateField(validators=[adult_validator], verbose_name='Date Of Birth',
                                     help_text='You must be above 18 years of age.')

    street_number = models.CharField(max_length=200, blank=True, null=True, verbose_name='Street Number',
                                     help_text='This field is optional. Please enter your street number.')
    street_name = models.TextField(verbose_name='Street Name', help_text='Enter you Home Address.')
    apt_number = models.CharField(max_length=200, verbose_name='Apartment Number',
                                  help_text='Please enter your apartment number or house number.')
    city = models.CharField(max_length=200, validators=[alphabet_validator], verbose_name='City',
                            help_text='Please enter only alphabets.')
    state = models.CharField(max_length=200, validators=[alphabet_validator], verbose_name='State',
                             help_text='Please enter only alphabets.')
    country = CountryField(blank_label='Select Your Country')
    zip = models.CharField(max_length=6, validators=[zip_code_validator], verbose_name='Zip Code',
                           help_text='Please enter a 6 digit zip code.')

    def __str__(self):
        if self.middle_name:
            return self.first_name + ' ' + self.middle_name + ' ' + self.last_name
        else:
            return self.first_name + ' ' + self.last_name


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Staff")
    email = models.EmailField(unique=True, help_text='Enter a valid email address.')
    first_name = models.CharField(max_length=200, validators=[alphabet_validator], verbose_name='First Name',
                                  help_text='Please enter only alphabets.')
    middle_name = models.CharField(max_length=200, blank=True, null=True, validators=[alphabet_validator],
                                   verbose_name='Middle Name',
                                   help_text='This field is optional. Please enter only alphabets.')
    last_name = models.CharField(max_length=200, validators=[alphabet_validator], verbose_name='Last Name',
                                 help_text='Please enter only alphabets.')
    date_of_birth = models.DateField(validators=[adult_validator], verbose_name='Date Of Birth',
                                     help_text='You must be above 18 years of age.')

    street_number = models.CharField(max_length=200, blank=True, null=True, verbose_name='Street Number',
                                     help_text='This field is optional. Please enter your street number.')
    street_name = models.TextField(verbose_name='Street Name', help_text='Enter you Home Address.')
    apt_number = models.CharField(max_length=200, verbose_name='Apartment Number',
                                  help_text='Please enter your apartment number or house number.')
    city = models.CharField(max_length=200, validators=[alphabet_validator], verbose_name='City',
                            help_text='Please enter only alphabets.')
    state = models.CharField(max_length=200, validators=[alphabet_validator], verbose_name='State',
                             help_text='Please enter only alphabets.')
    country = CountryField(blank_label='Select Your Country')
    zip = models.CharField(max_length=6, validators=[zip_code_validator], verbose_name='Zip Code',
                           help_text='Please enter a 6 digit zip code.')

    def __str__(self):
        if self.middle_name:
            return self.first_name + ' ' + self.middle_name + ' ' + self.last_name
        else:
            return self.first_name + ' ' + self.last_name


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Vendor")
    email = models.EmailField(unique=True, help_text='Enter a valid email address.')
    company_name = models.CharField(max_length=200, verbose_name='Company Name',
                                    help_text='Please enter your company name.')

    street_number = models.CharField(max_length=200, blank=True, null=True, verbose_name='Street Number',
                                     help_text='This field is optional. Please enter your street number.')
    street_name = models.TextField(verbose_name='Street Name', help_text='Enter you Home Address.')
    building_number = models.CharField(max_length=200, verbose_name='Building Number',
                                       help_text='Please enter your building number.')
    city = models.CharField(max_length=200, validators=[alphabet_validator], verbose_name='City',
                            help_text='Please enter only alphabets.')
    state = models.CharField(max_length=200, validators=[alphabet_validator], verbose_name='State',
                             help_text='Please enter only alphabets.')
    country = CountryField(blank_label='Select Your Country')
    zip = models.CharField(max_length=6, validators=[zip_code_validator], verbose_name='Zip Code',
                           help_text='Please enter a 6 digit zip code.')

    def __str__(self):
        return self.company_name
