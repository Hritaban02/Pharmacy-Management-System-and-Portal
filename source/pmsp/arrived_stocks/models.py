from accounts.models import Staff, Vendor
from django.db import models
from item.models import Item
from stock_requests.models import Stock_Request


# Create your models here.
class Arrived_Stock(models.Model):
    staff_id = models.ForeignKey(Staff, null=True, on_delete=models.SET_NULL)
    vendor_id = models.ForeignKey(Vendor, null=True, on_delete=models.SET_NULL)
    stock_request_id = models.OneToOneField(Stock_Request, null=True, on_delete=models.SET_NULL)
    creation_date_time = models.DateTimeField(auto_now_add=True)


class Arrived_Stock_Consists_Of(models.Model):
    arrived_stock_id = models.ForeignKey(Arrived_Stock, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("arrived_stock_id", "item_id"),)
        verbose_name = 'Arrived Stock Consists Of'
        verbose_name_plural = 'Arrived Stock Consists Of'
