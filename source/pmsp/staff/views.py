import datetime

from accounts.models import Staff, Vendor
from arrived_stocks.models import Arrived_Stock, Arrived_Stock_Consists_Of
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse
from item.models import Item
from medicine.models import Medicine
from orders.models import Order, Order_On_Medicine, Order_Consists_Of
from phone_number.models import Customer_Phone, Vendor_Phone
from stock_requests.models import Stock_Request, Stock_Request_Consists_Of


def check_and_update_expired_items():
    expiry_date = datetime.date.today()
    expired_items = Item.objects.filter(usable_quantity__gt=0, expiry_date__lte=expiry_date)
    for item in expired_items:
        item_object = Item.objects.get(id=item.id)
        usable_quantity = item_object.usable_quantity
        item_object.expired_quantity += usable_quantity
        item_object.usable_quantity = 0
        item_object.save()


def is_staff(user):
    try:
        staff_object = Staff.objects.get(user=user)
    except Staff.DoesNotExist:
        staff_object = None
    return user.is_authenticated and staff_object is not None


def is_medicine_in_any_stock_request(medicine_id):
    stock_requests = Stock_Request.objects.filter(accept_status="Pending")
    for stock_request in stock_requests:
        medicine_in_stock_request = Stock_Request_Consists_Of.objects.filter(
            stock_request_id=stock_request.id)

        for medicine in medicine_in_stock_request:
            if int(medicine_id) == int(medicine.medicine_id.id):
                return True

    return False


# Create your views here.
@login_required(login_url='accounts:login')
@user_passes_test(is_staff)
def index(request):
    order_list = None
    error_message = None
    order_on_medicine_list = {}
    total_price_list = {}
    if request.user.is_authenticated:
        try:
            staff_object = Staff.objects.get(user=request.user)
        except Staff.DoesNotExist:
            staff_object = None
    else:
        staff_object = None

    if request.method == 'POST' and staff_object is not None:
        accept = request.POST.get('accept', 0)

        if accept != 0:
            return redirect(reverse('staff:accept_order') + '?id=' + str(accept))

    if staff_object is not None:
        try:
            order_list = Order.objects.filter(placed=True).order_by('-order_date_time')
        except Order.DoesNotExist:
            error_message = "No Orders Arrived Yet"
            order_list = None
            order_on_medicine_list = None

        if order_list.exists():
            subset = request.GET.get('subset', 0)
            if subset == 'a':
                order_list = order_list.filter(status="Accepted")
                error_message = "No Orders Accepted Yet"
            elif subset == 'd':
                order_list = order_list.filter(status="Delivered")
                error_message = "No Orders Delivered Yet"
            elif subset == 'p':
                order_list = order_list.filter(status="Pending")
                error_message = "No Orders Pending Yet"

            for order in order_list:
                order_on_medicine_list[order.id] = Order_On_Medicine.objects.filter(order_id=order.id)
                total_price = 0
                for medicine in order_on_medicine_list[order.id]:
                    total_price += medicine.quantity * medicine.selling_price_at_time_of_order

                total_price_list[order.id] = total_price
        else:
            error_message = "No Orders Arrived Yet"

    template = loader.get_template('staff/index.html')
    context = {
        "order_list": order_list,
        "order_on_medicine_list": order_on_medicine_list,
        "total_price_list": total_price_list,
        "error_message": error_message,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_staff)
def stock_requests_made(request):
    arrived = None
    stock_requests = None
    medicine_in_stock_request = None
    total_price_list = None
    error_message = None
    staff_id = None
    vendor_phone = None

    if request.user.is_authenticated:
        try:
            staff_object = Staff.objects.get(user=request.user)
            staff_id = staff_object
        except Staff.DoesNotExist:
            staff_object = None
    else:
        staff_object = None

    cancel = request.POST.get("cancel", -1)
    if cancel != -1:
        stock_request_to_delete = Stock_Request.objects.get(id=int(cancel))
        stock_request_to_delete.delete()

    if staff_object is not None:
        stock_requests = Stock_Request.objects.filter(staff_id=staff_id)

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
            arrived = {}
            total_price_list = {}
            vendor_phone = {}
            for stock_request in stock_requests:
                medicine_in_stock_request[stock_request.id] = Stock_Request_Consists_Of.objects.filter(
                    stock_request_id=stock_request.id)

                total_price = 0
                for medicine in medicine_in_stock_request[stock_request.id]:
                    total_price += medicine.quantity * medicine.cost_price_at_time_of_request

                total_price_list[stock_request.id] = total_price

                try:
                    arrived_stock_object = Arrived_Stock.objects.get(stock_request_id=stock_request.id)

                except Arrived_Stock.DoesNotExist:
                    arrived_stock_object = None

                arrived[stock_request.id] = arrived_stock_object is not None

                vendor_phone[stock_request.id] = Vendor_Phone.objects.filter(vendor_id=stock_request.vendor_id.id)
        else:
            error_message = "No Stock Requests Sent"
    template = loader.get_template('staff/stock_requests_made.html')
    context = {
        "stock_requests": stock_requests,
        "medicine_in_stock_request": medicine_in_stock_request,
        "total_price_list": total_price_list,
        "arrived": arrived,
        "vendor_phone": vendor_phone,
        "error_message": error_message,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_staff)
def new_stock_request(request):
    RISK_THRESHOLD = int(request.POST.get("risk_threshold", 50))
    RISK_THRESHOLD = int(request.GET.get("risk_threshold", RISK_THRESHOLD))
    button_click = request.POST.get('set_risk_threshold', -1)

    if button_click != -1:
        return redirect(reverse('staff:new_stock_request') + '?risk_threshold=' + str(RISK_THRESHOLD))

    vendor_selected = request.POST.get("vendor_selected", -1)
    create = request.POST.get("create", -1)
    all_medicines = Medicine.objects.all()
    staff_id = None
    error_message = None
    new_stock_request_id = None
    vendor_object = None
    usable_items_for_all_medicines = {}
    medicines_at_risk = {}

    if request.user.is_authenticated:
        try:
            staff_object = Staff.objects.get(user=request.user)
            staff_id = staff_object
        except Staff.DoesNotExist:
            staff_object = None
    else:
        staff_object = None

    if staff_object is not None:
        if vendor_selected != -1:
            try:
                vendor_object = Vendor.objects.get(id=vendor_selected)
            except ValueError:
                vendor_object = None

        for medicine in all_medicines:
            if medicine.id not in usable_items_for_all_medicines:
                usable_items_for_all_medicines[medicine.id] = 0
            for item in Item.objects.filter(medicine_id=medicine.id):
                usable_items_for_all_medicines[medicine.id] += item.usable_quantity

        for key in usable_items_for_all_medicines:
            value = usable_items_for_all_medicines[key]
            if value <= RISK_THRESHOLD and not is_medicine_in_any_stock_request(key):
                medicine_object = Medicine.objects.get(id=key)
                vendor = medicine_object.vendor_id
                if vendor not in medicines_at_risk:
                    medicines_at_risk[vendor] = []
                medicines_at_risk[vendor].append((medicine_object, value))

        if len(medicines_at_risk) == 0:
            medicines_at_risk = None
            error_message = "Congratulations! You have stocked up."

        if create == "1":
            vendor_id = request.POST.get("vendor_id", -1)
            try:
                vendor_object = Vendor.objects.get(id=int(vendor_id))
            except:
                raise Http404("Vendor Not Found")

            new_stock_request_object = Stock_Request.objects.create(staff_id=staff_id, vendor_id=vendor_object)
            new_stock_request_id = new_stock_request_object.id
            for medicine_to_stock, _ in medicines_at_risk[vendor_object]:
                cost_price = Medicine.objects.get(id=medicine_to_stock.id).cost_price
                quantity_to_stock = request.POST.get("quantity_" + str(medicine_to_stock.id), -1)
                if quantity_to_stock == -1:
                    raise Http404("Quantity is Negative")
                Stock_Request_Consists_Of.objects.create(stock_request_id=new_stock_request_object,
                                                         medicine_id=medicine_to_stock, quantity=quantity_to_stock,
                                                         cost_price_at_time_of_request=cost_price)

            new_stock_request_object.save()
            new_stock_request_consists_of = Stock_Request_Consists_Of.objects.filter(
                stock_request_id=new_stock_request_id)
            for medicine in new_stock_request_consists_of:
                medicine.save()

            return redirect('staff:stock_requests_made')

        if medicines_at_risk is None:
            error_message = "Congratulations! You have stocked up."

    template = loader.get_template('staff/new_stock_request.html')
    context = {
        "new_stock_request_id": new_stock_request_id,
        "medicines_at_risk": medicines_at_risk,
        "risk_threshold_value": RISK_THRESHOLD,
        "vendor_object": vendor_object,
        "error_message": error_message,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_staff)
@transaction.atomic
def accept_order(request):
    check_and_update_expired_items()
    phone_number_list = None
    unit_price_of_items = None
    items_in_order = None
    staff_id = None
    total_price = None
    if request.user.is_authenticated:
        try:
            staff_object = Staff.objects.get(user=request.user)
            staff_id = staff_object.id
        except Staff.DoesNotExist:
            staff_object = None
    else:
        staff_object = None

    order_id = request.GET.get('id', -1)

    if order_id != -1:
        order_to_accept = Order.objects.get(id=order_id)
        medicines_required = Order_On_Medicine.objects.filter(order_id=order_id)

        medicines_in_stock = {}
        medicines_out_of_stock = []
        for medicine in medicines_required:
            medicine_id = medicine.medicine_id
            available_items = Item.objects.filter(medicine_id=medicine_id, usable_quantity__gt=0)

            if medicine_id not in medicines_in_stock:
                medicines_in_stock[medicine_id] = 0

            for item in available_items:
                medicines_in_stock[medicine_id] += item.usable_quantity

            quantity_required = medicine.quantity
            quantity_available = medicines_in_stock[medicine_id]
            if quantity_required > quantity_available:
                medicines_out_of_stock.append(
                    (medicine_id.id, medicine_id.trade_name, quantity_available, quantity_required))

        if medicines_out_of_stock is None or len(medicines_out_of_stock) == 0:
            for medicine in medicines_required:
                medicine_id = medicine.medicine_id
                available_items = Item.objects.filter(medicine_id=medicine_id)

                quantity_required = medicine.quantity
                i = 0
                while quantity_required != 0:
                    if available_items[i].usable_quantity >= quantity_required:
                        new_item_object = Order_Consists_Of.objects.create(order_id=order_to_accept,
                                                                           item_id=available_items[i],
                                                                           quantity=quantity_required)
                        item_to_update = Item.objects.get(id=available_items[i].id)
                        item_to_update.usable_quantity = F('usable_quantity') - quantity_required
                        item_to_update.save()
                        new_item_object.save()
                        quantity_required -= quantity_required
                    elif available_items[i].usable_quantity > 0:
                        new_item_object = Order_Consists_Of.objects.create(order_id=order_to_accept,
                                                                           item_id=available_items[i],
                                                                           quantity=available_items[i].usable_quantity)
                        quantity_required -= available_items[i].usable_quantity
                        item_to_update = Item.objects.get(id=available_items[i].id)
                        item_to_update.usable_quantity = 0
                        item_to_update.save()

                        new_item_object.save()
                    i += 1

            order_to_accept.status = "Accepted"
            order_to_accept.staff_id = staff_object
            order_to_accept.process_start_date = datetime.date.today()
            order_to_accept.save()

            items_in_order = Order_Consists_Of.objects.filter(order_id=order_id)
            unit_price_of_items = {}
            total_price = 0
            for item in items_in_order:
                unit_price_of_items[item] = Order_On_Medicine.objects.get(order_id=order_id,
                                                                          medicine_id=item.item_id.medicine_id).selling_price_at_time_of_order
                total_price += item.quantity * unit_price_of_items[item]

            phone_number_list = []
            for phone in Customer_Phone.objects.filter(customer_id=order_to_accept.customer_id.id):
                phone_number_list.append(phone.phone_number)

        template = loader.get_template('staff/accept_order.html')
        context = {
            'order_id': order_id,
            'order_to_accept': order_to_accept,
            'staff_id': staff_id,
            'staff_object': staff_object,
            'medicines_required': medicines_required,
            'items_in_order': items_in_order,
            'unit_price_of_items': unit_price_of_items,
            'total_price': total_price,
            'phone_number_list': phone_number_list,
            'medicines_out_of_stock': medicines_out_of_stock,
        }
        return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_staff)
def order_details(request):
    staff_id = None
    if request.user.is_authenticated:
        try:
            staff_object = Staff.objects.get(user=request.user)
            staff_id = staff_object.id
        except Staff.DoesNotExist:
            staff_object = None
    else:
        staff_object = None

    order_id = request.GET.get('id', -1)

    if order_id != -1:
        order_to_accept = Order.objects.get(id=order_id)

        items_in_order = Order_Consists_Of.objects.filter(order_id=order_id)
        unit_price_of_items = {}
        total_price = 0
        for item in items_in_order:
            unit_price_of_items[item] = Order_On_Medicine.objects.get(order_id=order_id,
                                                                      medicine_id=item.item_id.medicine_id).selling_price_at_time_of_order
            total_price += item.quantity * unit_price_of_items[item]

        phone_number_list = []
        for phone in Customer_Phone.objects.filter(customer_id=order_to_accept.customer_id.id):
            phone_number_list.append(phone.phone_number)

        template = loader.get_template('staff/order_details.html')
        context = {
            'order_id': order_id,
            'order_to_accept': order_to_accept,
            'staff_id': staff_id,
            'staff_object': staff_object,
            'items_in_order': items_in_order,
            'unit_price_of_items': unit_price_of_items,
            'total_price': total_price,
            'phone_number_list': phone_number_list,
        }
        return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_staff)
def arrived_stock(request):
    items_in_arrived_stock = None
    vendor_phone = None
    stock_request_object = None
    arrived_stock_object = None
    medicine_in_stock_request = None
    if request.user.is_authenticated:
        try:
            staff_object = Staff.objects.get(user=request.user)
        except Staff.DoesNotExist:
            staff_object = None
    else:
        staff_object = None

    stock_request_id = request.GET.get('stock_request_id', -1)
    if stock_request_id != -1:
        stock_request_object = Stock_Request.objects.get(id=stock_request_id)
        medicine_in_stock_request = Stock_Request_Consists_Of.objects.filter(stock_request_id=stock_request_id)

        try:
            arrived_stock_object = Arrived_Stock.objects.get(stock_request_id=stock_request_id)
        except Arrived_Stock.DoesNotExist:
            arrived_stock_object = Arrived_Stock.objects.create(staff_id=staff_object,
                                                                vendor_id=stock_request_object.vendor_id,
                                                                stock_request_id=stock_request_object)

        medicine_id = request.POST.get('medicine_id', -1)
        quantity = request.POST.get('quantity', -1)
        expiry_date = request.POST.get('expiry_date', -1)

        if medicine_id != -1 and quantity != -1 and expiry_date != -1:
            medicine_object = Medicine.objects.get(id=medicine_id)
            item_object = Item.objects.create(medicine_id=medicine_object, expiry_date=expiry_date,
                                              quantity_at_time_of_arrival=quantity, usable_quantity=quantity)
            item_object.save()

            arrived_stock_consists_of_object = Arrived_Stock_Consists_Of.objects.create(item_id=item_object,
                                                                                        arrived_stock_id=arrived_stock_object)
            arrived_stock_consists_of_object.save()

        vendor_phone = Vendor_Phone.objects.filter(vendor_id=stock_request_object.vendor_id.id)

        items_in_arrived_stock = Arrived_Stock_Consists_Of.objects.filter(arrived_stock_id=arrived_stock_object.id)

    template = loader.get_template('staff/arrived_stock.html')
    context = {
        'stock_request': stock_request_object,
        'arrived_stock_object': arrived_stock_object,
        'staff_object': staff_object,
        'vendor_phone': vendor_phone,
        'items_in_arrived_stock': items_in_arrived_stock,
        'medicine_in_stock_request': medicine_in_stock_request,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_staff)
def arrived_stock_details(request):
    stock_request_object = None
    medicine_in_stock_request = None
    arrived_stock_object = None
    vendor_phone = None
    items_in_arrived_stock = None
    staff_id = None
    if request.user.is_authenticated:
        try:
            staff_object = Staff.objects.get(user=request.user)
            staff_id = staff_object.id
        except Staff.DoesNotExist:
            staff_object = None
    else:
        staff_object = None

    stock_request_id = request.GET.get('stock_request_id', -1)
    if stock_request_id != -1:
        stock_request_object = Stock_Request.objects.get(id=stock_request_id)
        medicine_in_stock_request = Stock_Request_Consists_Of.objects.filter(stock_request_id=stock_request_id)
        arrived_stock_object = Arrived_Stock.objects.get(stock_request_id=stock_request_id)
        vendor_phone = Vendor_Phone.objects.filter(vendor_id=arrived_stock_object.vendor_id.id)
        items_in_arrived_stock = Arrived_Stock_Consists_Of.objects.filter(arrived_stock_id=arrived_stock_object.id)

    template = loader.get_template('staff/arrived_stock_details.html')
    context = {
        'stock_request': stock_request_object,
        'arrived_stock_object': arrived_stock_object,
        'staff_object': staff_object,
        'staff_id': staff_id,
        'vendor_phone': vendor_phone,
        'items_in_arrived_stock': items_in_arrived_stock,
        'medicine_in_stock_request': medicine_in_stock_request,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_staff)
def expired_item_details(request):
    check_and_update_expired_items()
    month = int(request.GET.get('month', -1))
    year = int(request.GET.get('year', -1))
    staff_id = None
    if request.user.is_authenticated:
        try:
            staff_object = Staff.objects.get(user=request.user)
            staff_id = staff_object.id
        except Staff.DoesNotExist:
            staff_object = None
    else:
        staff_object = None

    if month != -1 and year != -1:
        expired_items = Item.objects.filter(expiry_date__month=month, expiry_date__year=year, expired_quantity__gt=0)
    else:
        expired_items = None
        month = None
        year = None

    template = loader.get_template('staff/expired_item_details.html')
    context = {
        'staff_object': staff_object,
        'staff_id': staff_id,
        'expired_items': expired_items,
        'month_entered': month,
        'year_entered': year,
    }
    return HttpResponse(template.render(context, request))
