import datetime

from accounts.models import Staff, Vendor
from django.core.validators import MinValueValidator
from django.db import models
from medicine.models import Medicine


def get_default_estimated_send_date():
    return datetime.date.today() + datetime.timedelta(7)


# Create your models here.
class Stock_Request(models.Model):
    ACCEPT_STATUS_CHOICES = (
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
        ("Pending", "Pending"),
    )

    staff_id = models.ForeignKey(Staff, null=True, on_delete=models.SET_NULL)
    vendor_id = models.ForeignKey(Vendor, null=True, on_delete=models.SET_NULL)
    creation_date_time = models.DateTimeField(auto_now_add=True)
    accept_status = models.CharField(blank=True, max_length=32, choices=ACCEPT_STATUS_CHOICES, default='Pending',
                                     null=True, verbose_name='Accept Status', help_text="Choose a status")
    estimated_send_date = models.DateField(blank=True, null=True, default=get_default_estimated_send_date)


class Stock_Request_Consists_Of(models.Model):
    stock_request_id = models.ForeignKey(Stock_Request, on_delete=models.CASCADE)
    medicine_id = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(0)],
                                   verbose_name='Quantity',
                                   help_text='Quantity of the Medicine requested.')
    cost_price_at_time_of_request = models.DecimalField(decimal_places=2, max_digits=19,
                                                        validators=[MinValueValidator(0.0)],
                                                        verbose_name='Cost Price',
                                                        help_text='Cost Price of the Medicine at time of request.')

    class Meta:
        unique_together = (("stock_request_id", "medicine_id"),)
        verbose_name = 'Stock Request Consists Of'
        verbose_name_plural = 'Stock Request Consists Of'
