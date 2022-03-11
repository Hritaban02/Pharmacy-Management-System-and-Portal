from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse
from medicine.views import is_customer
from phone_number.models import phone_number_validator, Customer_Phone
from staff.views import is_staff
from vendor.views import is_vendor

from .forms import PasswordChangingForm, UserForm, RegisterCustomerForm
from .models import Customer, Vendor, Staff


# Create your views here.
def login_excluded(redirect_to):
    """ This decorator kicks authenticated users out of a view """

    def _method_wrapper(view_method):
        def _arguments_wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_to)
            return view_method(request, *args, **kwargs)

        return _arguments_wrapper

    return _method_wrapper


def login_page(request, backend=None):
    successful_registration = request.GET.get('success', -1)
    success_message = None
    if successful_registration != -1:
        success_message = "Registration Successful! Please Login."

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                customer_object = Customer.objects.get(user=request.user)
            except Customer.DoesNotExist:
                customer_object = None

            if customer_object is not None:
                return redirect('medicine:index')

            try:
                vendor_object = Vendor.objects.get(user=request.user)
            except Vendor.DoesNotExist:
                vendor_object = None

            if vendor_object is not None:
                return redirect('vendor:index')

            try:
                staff_object = Staff.objects.get(user=request.user)
            except Staff.DoesNotExist:
                staff_object = None

            if staff_object is not None:
                return redirect('staff:index')

            if request.user.is_active and request.user.is_superuser:
                return redirect(reverse('admin:index'))

            return redirect('medicine:index')
        else:
            messages.info(request, 'Username or Password is incorrect.')
    else:
        list(messages.get_messages(request))
    template = loader.get_template('accounts/login_page.html')
    context = {
        'success_message': success_message,
    }
    return HttpResponse(template.render(context, request))


def register(request):
    error_message = []
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        user_form = UserForm(request.POST)
        customer_form = RegisterCustomerForm(request.POST)

        # check whether it's valid:
        if user_form.is_valid() and customer_form.is_valid():
            # process the data in form.cleaned_data as required
            user_form_data = user_form.data
            try:
                new_user = User.objects.create_user(username=user_form_data['username'],
                                                    password=user_form_data['password'])
            except IntegrityError:
                new_user = None
                error_message.append("Please pick another username")
            except:
                new_user = None
                error_message.append("Could not create User. Please check your username and password.")

            if new_user is not None:
                try:
                    new_customer = Customer.objects.create(user=new_user, email=user_form_data['email'],
                                                           first_name=user_form_data['first_name'],
                                                           middle_name=user_form_data['middle_name'],
                                                           last_name=user_form_data['last_name'],
                                                           date_of_birth=date(int(user_form_data['date_of_birth_year']),
                                                                              int(user_form_data[
                                                                                      'date_of_birth_month']),
                                                                              int(user_form_data['date_of_birth_day'])),
                                                           street_number=user_form_data['street_number'],
                                                           street_name=user_form_data['street_name'],
                                                           apt_number=user_form_data['apt_number'],
                                                           city=user_form_data['city'],
                                                           state=user_form_data['state'],
                                                           country=user_form_data['country'],
                                                           zip=user_form_data['zip'])
                except:
                    new_customer = None
                    new_user.delete()
                    error_message.append('Could not create Customer. Please check all your entries.')

                if new_customer is not None:
                    phone_number1 = user_form_data['phone_number1']
                    try:
                        phone_number_validator(phone_number1)
                        phone_number1_object = Customer_Phone.objects.create(customer_id=new_customer.id,
                                                                             phone_number=phone_number1)
                    except ValidationError:
                        phone_number1_object = None
                        error_message.append("Invalid phone number: Must be only 10 digits long.")
                    except:
                        phone_number1_object = None
                        error_message.append("Please enter your phone number only.")

                    if phone_number1_object is not None:
                        if user_form_data.get('phone_number2', None) is not None:
                            phone_number2 = user_form_data['phone_number2']
                            try:
                                phone_number_validator(phone_number2)
                                phone_number2_object = Customer_Phone.objects.create(customer_id=new_customer.id,
                                                                                     phone_number=phone_number2)
                            except ValidationError:
                                phone_number2_object = None
                                error_message.append("Invalid phone number: Must be only 10 digits long.")
                            except:
                                phone_number2_object = None
                                error_message.append("Please enter your phone number only.")

                            if phone_number2_object is not None:
                                new_user.save()
                                new_customer.save()
                                phone_number1_object.save()
                                phone_number2_object.save()

                                # redirect to a new URL:
                                return redirect(reverse('accounts:login') + '?success=1')
                            else:
                                phone_number1_object.delete()
                                new_customer.delete()
                                new_user.delete()
                        else:
                            new_user.save()
                            new_customer.save()
                            phone_number1_object.save()

                            # redirect to a new URL:
                            return redirect(reverse('accounts:login') + '?success=1')

                    else:
                        new_user.delete()
                        new_customer.delete()

    # if a GET (or any other method) we'll create a blank form
    else:
        list(messages.get_messages(request))
        user_form = UserForm()
        customer_form = RegisterCustomerForm()
    template = loader.get_template('accounts/register.html')
    context = {
        'user_form': user_form,
        'customer_form': customer_form,
        'error_message': error_message,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_customer)
def update_customer_details(request):
    error_message = []
    if request.user.is_authenticated:
        try:
            customer_object = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            customer_object = None
    else:
        customer_object = None

    if request.method == 'POST' and customer_object is not None:
        customer_form = RegisterCustomerForm(request.POST)

        for phone_number_object in Customer_Phone.objects.filter(customer_id=customer_object.id):
            new_phone_number_val = request.POST.get(str(phone_number_object.id), None)
            if new_phone_number_val is not None:
                try:
                    phone_number_validator(new_phone_number_val)
                except ValidationError:
                    error_message.append("Invalid phone number: Must be only 10 digits long.")
                setattr(phone_number_object, "phone_number", new_phone_number_val)
                phone_number_object.save()

        if customer_form.is_valid():
            customer_form_data = customer_form.data
            for k, v in dict(customer_form_data).items():
                setattr(customer_object, k, v[0])
            customer_object.save()

    customer_form = RegisterCustomerForm(initial=customer_object.__dict__)
    try:
        phone_numbers = Customer_Phone.objects.filter(customer_id=customer_object.id)
    except:
        phone_numbers = None
        error_message.append("Could not fetch phone numbers.")

    print(phone_numbers)

    template = loader.get_template('accounts/update_customer_details.html')
    context = {
        'customer_form': customer_form,
        'phone_numbers': phone_numbers,
        'error_message': error_message,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
def logout_user(request):
    logout(request)
    return redirect('home:index')


@login_required(login_url='accounts:login')
def change_password(request):
    current_password = request.user.password  # user's current password

    form = PasswordChangingForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            current_password_entered = form.cleaned_data.get("old_password")
            password1 = form.cleaned_data.get("new_password1")
            password2 = form.cleaned_data.get("new_password2")

            match_check = check_password(current_password_entered, current_password)
            if match_check:
                if password1 == password2:
                    u = request.user
                    u.set_password(password1)
                    u.save()
                    messages.success(request, 'Password Was Changed Successfully.')
                    return redirect('medicine:index')
                else:
                    messages.success(request, 'New Passwords do not match.')
            else:
                messages.success(request, 'Old Password is incorrect.')
        else:
            messages.success(request, 'Passwords not Valid.')
    template = loader.get_template('accounts/change_password.html')
    if is_customer(request.user):
        base = 'base.html'
    elif is_vendor(request.user):
        base = 'vendor_base.html'
    elif is_staff(request.user):
        base = 'staff_base.html'
    context = {
        "base": base,
    }
    return HttpResponse(template.render(context, request))
