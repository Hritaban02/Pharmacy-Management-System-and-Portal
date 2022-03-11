from django.http import Http404
from django.http import HttpResponse
from django.template import loader
from medicine.models import Medicine


def gte_avg_rating_query_set(query_set, decimal_value):
    new_query_set = []
    for item in query_set:
        if item.avg_rating >= decimal_value:
            new_query_set.append(item)

    return new_query_set


# Create your views here.
def index(request):
    if request.method == "GET":
        medicine_query_set = Medicine.objects.all()
        template = loader.get_template('home/index.html')

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


def search(request):
    if request.method == "GET":
        search_term = request.GET.get('search')
        medicine_query_set = Medicine.objects.all().filter(
            trade_name__icontains=search_term) | Medicine.objects.all().filter(scientific_name__icontains=search_term)
        template = loader.get_template('home/index.html')

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


def detail(request, medicine_id):
    try:
        medicine_object = Medicine.objects.get(id=medicine_id)
    except Medicine.DoesNotExist:
        raise Http404("Medicine does not exist")

    if request.method == "GET":
        pass

    template = loader.get_template('home/detail.html')
    context = {
        'medicine_object': medicine_object,
    }
    return HttpResponse(template.render(context, request))
