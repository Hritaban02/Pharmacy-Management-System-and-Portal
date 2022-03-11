from django.urls import path

from . import views

app_name = 'orders'
urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('my_orders/', views.my_orders, name='my_orders')
]
