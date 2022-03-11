from datetime import date

from django import forms
from django.contrib.auth.models import User
from django_countries.fields import CountryField

from .models import Customer, adult_validator, alphabet_validator, zip_code_validator

YEAR_CHOICES = tuple([*range(date.today().year, date.today().year - 200, -1)])


class PasswordChangingForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))

    class Meta:
        model = User
        fields = '__all__'


class UserForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'username'}),
                               help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
                               help_text="Your password can’t be too similar to your other personal information. \nYour password must contain at least 8 characters. \nYour password can’t be a commonly used password. \nYour password can’t be entirely numeric.")

    class Meta:
        model = User
        fields = '__all__'


class RegisterCustomerForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'type': 'email'}),
                             help_text='Enter a valid email address.')
    first_name = forms.CharField(validators=[alphabet_validator],
                                 widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 help_text='Please enter only alphabets.')
    middle_name = forms.CharField(validators=[alphabet_validator], required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}),
                                  help_text='This field is optional. Please enter only alphabets.')
    last_name = forms.CharField(validators=[alphabet_validator],
                                widget=forms.TextInput(attrs={'class': 'form-control'}),
                                help_text='Please enter only alphabets.')
    date_of_birth = forms.DateField(validators=[adult_validator], widget=forms.SelectDateWidget(years=YEAR_CHOICES),
                                    help_text='You must be above 18 years of age.')
    street_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}),
                                    help_text='This field is optional. Please enter your street number.')
    street_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                  help_text='Enter you Home Address.')
    apt_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 help_text='Please enter your apartment number or house number.')
    city = forms.CharField(validators=[alphabet_validator], widget=forms.TextInput(attrs={'class': 'form-control'}),
                           help_text='Please enter only alphabets.')
    state = forms.CharField(validators=[alphabet_validator], widget=forms.TextInput(attrs={'class': 'form-control'}),
                            help_text='Please enter only alphabets.')
    country = CountryField().formfield()
    zip = forms.CharField(validators=[zip_code_validator], widget=forms.TextInput(attrs={'class': 'form-control'}),
                          help_text='Please enter a 6 digit zip code.')

    class Meta:
        model = Customer
        fields = '__all__'
