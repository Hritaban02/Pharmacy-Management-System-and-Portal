import datetime

from accounts.models import Customer, Staff
from django.core.validators import MinValueValidator
from django.db import models
from item.models import Item
from medicine.models import Medicine


def get_default_estimated_delivery_date():
    return datetime.date.today() + datetime.timedelta(7)


# Create your models here.
class Order(models.Model):
    PAYMENT_CHOICES = (
        ("Card", "Payment via Credit Card"),
        ("Cash on Delivery", "Payment on Delivery"),
    )
    STATUS_CHOICES = (
        ("Pending", "Pending to be accepted by Staff"),
        ("Accepted", "Accepted by a Staff member"),
        ("Delivered", "Delivered to the Customer"),
    )
    staff_id = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL)
    customer_id = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    order_date_time = models.DateTimeField(auto_now_add=True)
    placed = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=32, choices=PAYMENT_CHOICES, default='Cash on Delivery', null=True,
                                      verbose_name='Payment Method', help_text='Choose an appropriate payment method.')
    process_start_date = models.DateField(blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, default=get_default_estimated_delivery_date)
    status = models.CharField(blank=True, max_length=32, choices=STATUS_CHOICES, default='Pending', null=True,
                              verbose_name='Status', help_text='Check Status')

    def __str__(self):
        return "Order " + str(self.id) + '---' + str(self.customer_id) + '---' + str(self.order_date_time)


class Order_On_Medicine(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    medicine_id = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(0)],
                                   verbose_name='Quantity',
                                   help_text='Quantity of the Medicine ordered.')
    selling_price_at_time_of_order = models.DecimalField(decimal_places=2, max_digits=19,
                                                         validators=[MinValueValidator(0.0)],
                                                         verbose_name='Selling Price',
                                                         help_text='Selling Price of the Medicine at time of order.')

    def __str__(self):
        return "Order " + str(self.order_id) + '---' + str(self.medicine_id)


class Order_Consists_Of(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(0)],
                                   verbose_name='Quantity',
                                   help_text='Quantity of the Medicine obtained from this item.')

    class Meta:
        unique_together = (("order_id", "item_id"),)
        verbose_name = 'Order Consists Of'
        verbose_name_plural = 'Order Consists Of'
