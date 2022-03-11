import datetime

from accounts.models import Customer
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.utils import timezone
from medicine.views import is_customer

from .models import Order, Order_On_Medicine


# Create your views here.
@login_required(login_url='accounts:login')
@user_passes_test(is_customer)
def cart(request):
    total_price = None
    medicines_in_cart = None
    error_message = None
    if request.user.is_authenticated:
        try:
            customer_object = Customer.objects.get(user=request.user)
            customer_id = customer_object.id
        except Customer.DoesNotExist:
            customer_object = None
    else:
        customer_object = None

    if customer_object is not None:
        try:
            my_cart = Order.objects.get(customer_id=customer_id, placed=False)
        except Order.DoesNotExist:
            error_message = "No Items in Cart"
            medicines_in_cart = None
            my_cart = None
        except Order.MultipleObjectsReturned:
            raise Http404("System Error Has Occurred : Multiple unplaced Orders")
            medicines_in_cart = None
            my_cart = None

        if my_cart is not None:
            medicines_in_cart = Order_On_Medicine.objects.filter(order_id=my_cart.id)

    if request.method == 'GET':
        pass

    if request.method == 'POST' and customer_object is not None:
        place = request.POST.get('place', 0)
        payment = request.POST.get('payment', 0)

        if place == '1' and payment != 0:
            order_to_place = Order.objects.get(id=my_cart.id)
            order_to_place.order_date_time = timezone.now()
            order_to_place.placed = True
            if payment == '1':
                order_to_place.payment_method = "Cash on Delivery"
            elif payment == '2':
                order_to_place.payment_method = "Card"
            order_to_place.save()

            return redirect('orders:my_orders')
        else:
            delete = request.POST.get('delete', -1)

            if delete != -1:
                medicine_to_delete = Order_On_Medicine.objects.get(order_id=my_cart.id, medicine_id=delete)
                medicine_to_delete.delete()

            new_quantity = request.POST.get('quantity', -1)
            update = request.POST.get('update', -1)

            if new_quantity != -1 and update != -1:
                medicine_to_update = Order_On_Medicine.objects.get(order_id=my_cart.id, medicine_id=update)
                medicine_to_update.quantity = new_quantity
                medicine_to_update.save()

        try:
            my_cart = Order.objects.get(customer_id=customer_id, placed=False)
        except Order.DoesNotExist:
            error_message = "No Items in Cart"
            medicines_in_cart = None
            my_cart = None
        except Order.MultipleObjectsReturned:
            raise Http404("System Error Has Occurred : Multiple unplaced Orders")
            medicines_in_cart = None
            my_cart = None

        if my_cart is not None:
            medicines_in_cart = Order_On_Medicine.objects.filter(order_id=my_cart.id)

    if medicines_in_cart is not None:
        total_price = 0
        for medicine in medicines_in_cart:
            total_price += medicine.quantity * medicine.selling_price_at_time_of_order

    template = loader.get_template('orders/cart.html')
    context = {
        "medicines_in_cart": medicines_in_cart,
        "total_price": total_price,
        "error_message": error_message,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_customer)
def my_orders(request):
    order_list = None
    error_message = None
    customer_id = None
    order_on_medicine_list = {}
    total_price_list = {}
    if request.user.is_authenticated:
        try:
            customer_object = Customer.objects.get(user=request.user)
            customer_id = customer_object.id
        except Customer.DoesNotExist:
            customer_object = None
    else:
        customer_object = None

    if request.method == 'GET':
        pass

    if request.method == 'POST' and customer_object is not None:
        cancel = request.POST.get("cancel", 0)

        if cancel != 0:
            order_to_cancel = Order.objects.get(id=cancel)
            order_to_cancel.delete()

    if customer_object is not None:
        try:
            order_list = Order.objects.filter(customer_id=customer_id, placed=True).order_by('-order_date_time')
        except Order.DoesNotExist:
            error_message = "No Orders Placed Yet"
            order_list = None
            order_on_medicine_list = None

        if order_list.exists():
            for order in order_list:
                if datetime.date.today() >= order.estimated_delivery_date and order.status == "Accepted":
                    order.status = "Delivered"
                    order.save()
                order_on_medicine_list[order.id] = Order_On_Medicine.objects.filter(order_id=order.id)
                total_price = 0
                for medicine in order_on_medicine_list[order.id]:
                    total_price += medicine.quantity * medicine.selling_price_at_time_of_order

                total_price_list[order.id] = total_price
        else:
            error_message = "No Orders Placed Yet"

    template = loader.get_template('orders/my_orders.html')
    context = {
        "order_list": order_list,
        "order_on_medicine_list": order_on_medicine_list,
        "total_price_list": total_price_list,
        "error_message": error_message,
    }
    return HttpResponse(template.render(context, request))
