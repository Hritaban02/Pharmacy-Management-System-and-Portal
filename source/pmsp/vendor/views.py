from accounts.models import Vendor, Staff
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.template import loader
from phone_number.models import Staff_Phone
from stock_requests.models import Stock_Request, Stock_Request_Consists_Of


def is_vendor(user):
    try:
        vendor_object = Vendor.objects.get(user=user)
    except Vendor.DoesNotExist:
        vendor_object = None
    return user.is_authenticated and vendor_object is not None


# Create your views here.
@login_required(login_url='accounts:login')
@user_passes_test(is_vendor)
def index(request):
    vendor_object = None
    error_message = None
    stock_requests = None
    medicine_in_stock_request = None
    total_price_list = None
    if request.user.is_authenticated:
        try:
            vendor_object = Vendor.objects.get(user=request.user)
        except Vendor.DoesNotExist:
            vendor_object = None

    if request.method == 'GET':
        pass

    if request.method == 'POST' and vendor_object is not None:
        accept = request.POST.get("accept", 0)
        reject = request.POST.get("reject", 0)

        if accept != 0:
            stock_request_to_accept = Stock_Request.objects.get(id=accept)
            stock_request_to_accept.accept_status = "Accepted"
            stock_request_to_accept.save()
        elif reject != 0:
            stock_request_to_accept = Stock_Request.objects.get(id=reject)
            stock_request_to_accept.accept_status = "Rejected"
            stock_request_to_accept.save()

    if vendor_object is not None:
        stock_requests = Stock_Request.objects.filter(vendor_id=vendor_object.id)

        if stock_requests.exists():
            subset = request.GET.get('subset', 0)

            if subset == 'a':
                stock_requests = stock_requests.filter(accept_status="Accepted")
                error_message = "No Stock Requests Accepted"
            elif subset == 'r':
                stock_requests = stock_requests.filter(accept_status="Rejected")
                error_message = "No Stock Requests Rejected"
            elif subset == 'p':
                stock_requests = stock_requests.filter(accept_status="Pending")
                error_message = "No Stock Requests Pending"

            stock_requests.order_by('-creation_date_time')

            medicine_in_stock_request = {}
            total_price_list = {}
            for stock_request in stock_requests:
                medicine_in_stock_request[stock_request.id] = Stock_Request_Consists_Of.objects.filter(
                    stock_request_id=stock_request.id)

                total_price = 0
                for medicine in medicine_in_stock_request[stock_request.id]:
                    total_price += medicine.quantity * medicine.cost_price_at_time_of_request

                total_price_list[stock_request.id] = total_price

        else:
            error_message = "No Stock Requests Received"

    template = loader.get_template('vendor/index.html')
    context = {
        "stock_requests": stock_requests,
        "medicine_in_stock_request": medicine_in_stock_request,
        "total_price_list": total_price_list,
        "error_message": error_message,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_vendor)
def staff_details(request):
    staff_id = request.GET.get('staff_id', -1)
    error_message = None
    staff_object = None
    staff_phone = None

    if staff_id != -1:
        try:
            staff_object = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            staff_object = None
            error_message = "Profile Not Found"

        if staff_object is not None:
            staff_phone = Staff_Phone.objects.filter(staff_id=staff_id)

    template = loader.get_template('vendor/staff_details.html')
    context = {
        "staff_object": staff_object,
        "staff_phone": staff_phone,
        "error_message": error_message,
    }
    return HttpResponse(template.render(context, request))
