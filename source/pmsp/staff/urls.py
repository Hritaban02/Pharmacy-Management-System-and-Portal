from django.urls import path

from . import views

app_name = 'staff'
urlpatterns = [
    path('', views.index, name='index'),
    path('stock_requests_made/', views.stock_requests_made, name='stock_requests_made'),
    path('new_stock_request/', views.new_stock_request, name='new_stock_request'),
    path('accept_order/', views.accept_order, name='accept_order'),
    path('order_details/', views.order_details, name='order_details'),
    path('arrived_stock/', views.arrived_stock, name='arrived_stock'),
    path('arrived_stock_details/', views.arrived_stock_details, name='arrived_stock_details'),
    path('expired_item_details/', views.expired_item_details, name='expired_item_details'),
]
