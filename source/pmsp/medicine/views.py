from accounts.models import Customer
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F
from django.http import Http404
from django.http import HttpResponse
from django.template import loader
from orders.models import Order, Order_On_Medicine

from .models import Medicine, Rate


def is_customer(user):
    try:
        customer_object = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        customer_object = None
    return user.is_authenticated and customer_object is not None


def gte_avg_rating_query_set(query_set, decimal_value):
    new_query_set = []
    for item in query_set:
        if item.avg_rating >= decimal_value:
            new_query_set.append(item)

    return new_query_set


# Create your views here.
@login_required(login_url='accounts:login')
@user_passes_test(is_customer)
def index(request):
    if request.method == "GET":
        medicine_query_set = Medicine.objects.all()
        template = loader.get_template('medicine/index.html')

        if request.GET.get('sort', 1) == '1':
            medicine_query_set = medicine_query_set.order_by('trade_name')
        elif request.GET.get('sort', 1) == '0':
            medicine_query_set = medicine_query_set.order_by('-trade_name')

        rating_filter = request.GET.get('rating', 0)

        if rating_filter == '1':
            medicine_query_set = gte_avg_rating_query_set(medicine_query_set, 1.0)
        elif rating_filter == '2':
            medicine_query_set = gte_avg_rating_query_set(medicine_query_set, 2.0)
        elif rating_filter == '3':
            medicine_query_set = gte_avg_rating_query_set(medicine_query_set, 3.0)
        elif rating_filter == '4':
            medicine_query_set = gte_avg_rating_query_set(medicine_query_set, 4.0)

        context = {
            'medicine_query_set': medicine_query_set,
            'error_message': 'Oops. Please check your filters and try again.',
        }
        return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_customer)
def search(request):
    if request.method == "GET":
        search_term = request.GET.get('search')
        medicine_query_set = Medicine.objects.all().filter(
            trade_name__icontains=search_term) | Medicine.objects.all().filter(scientific_name__icontains=search_term)
        template = loader.get_template('medicine/index.html')

        if request.GET.get('sort') == '1':
            medicine_query_set = medicine_query_set.order_by('trade_name')
        elif request.GET.get('sort') == '0':
            medicine_query_set = medicine_query_set.order_by('-trade_name')

        rating_filter = request.GET.get('rating', 0)

        if rating_filter == '1':
            medicine_query_set = gte_avg_rating_query_set(medicine_query_set, 1.0)
        elif rating_filter == '2':
            medicine_query_set = gte_avg_rating_query_set(medicine_query_set, 2.0)
        elif rating_filter == '3':
            medicine_query_set = gte_avg_rating_query_set(medicine_query_set, 3.0)
        elif rating_filter == '4':
            medicine_query_set = gte_avg_rating_query_set(medicine_query_set, 4.0)

        context = {
            'medicine_query_set': medicine_query_set,
            'search_term': search_term,
            'error_message': 'Oops. Please check your search term or adjust your filters and try again.',
        }
        return HttpResponse(template.render(context, request))


@login_required(login_url='accounts:login')
@user_passes_test(is_customer)
def detail(request, medicine_id):
    try:
        medicine_object = Medicine.objects.get(id=medicine_id)
    except Medicine.DoesNotExist:
        raise Http404("Medicine does not exist")

    if request.user.is_authenticated:
        try:
            customer_object = Customer.objects.get(user=request.user)
            customer_id = customer_object.id
        except Customer.DoesNotExist:
            customer_object = None

        if customer_object is not None:
            try:
                rating = Rate.objects.get(customer_id=customer_id, medicine_id=medicine_id)
            except Rate.DoesNotExist:
                rating = None
        else:
            rating = None
    else:
        customer_object = None
        rating = None

    if request.method == "GET":
        pass

    if request.method == 'POST' and customer_object is not None:
        selected_rate = request.POST.get('stars', 0)
        quantity = request.POST.get('quantity', 0)

        if selected_rate != 0:
            if rating is not None:
                rating.delete()

            new_rating = Rate(customer_id=customer_object, medicine_id=medicine_object, rating=selected_rate)
            new_rating.save()
            rating = Rate.objects.get(customer_id=customer_id, medicine_id=medicine_id)

        if quantity != 0:
            try:
                cart = Order.objects.get(customer_id=customer_id, placed=False)
            except Order.DoesNotExist:
                cart = Order.objects.create(customer_id=customer_object, placed=False)
                cart.save()
            except Order.MultipleObjectsReturned:
                raise Http404("System Error Has Occurred : Multiple unplaced Orders")

            try:
                medicine_in_cart = Order_On_Medicine.objects.get(order_id=cart.id, medicine_id=medicine_id)
            except Order_On_Medicine.DoesNotExist:
                medicine_in_cart = Order_On_Medicine.objects.create(order_id=cart, medicine_id=medicine_object,
                                                                    quantity=0,
                                                                    selling_price_at_time_of_order=medicine_object.selling_price)
            except Order_On_Medicine.MultipleObjectsReturned:
                raise Http404("System Error Has Occurred : Multiple Meds in Same Cart")

            additional_quantity = int(quantity)
            medicine_in_cart.quantity = F('quantity') + additional_quantity

            medicine_in_cart.save()

    template = loader.get_template('medicine/detail.html')
    context = {
        'medicine_object': medicine_object,
        'rating': rating,
        'customer': customer_object,
    }
    return HttpResponse(template.render(context, request))
