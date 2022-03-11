from django.core.validators import MinValueValidator
from django.db import models
from medicine.models import Medicine


# Create your models here.
class Item(models.Model):
    medicine_id = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    expiry_date = models.DateField(verbose_name='Expiry Date', help_text='Expiry Date of the Item')
    quantity_at_time_of_arrival = models.IntegerField(validators=[MinValueValidator(0)],
                                                      verbose_name='Quantity at time of Arrival',
                                                      help_text='Quantity of the item at the time arrival(sent by the vendor).')
    usable_quantity = models.IntegerField(validators=[MinValueValidator(0)],
                                          verbose_name='Usable Quantity',
                                          help_text='Usable Quantity of the Item left in stock.')
    expired_quantity = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)],
                                           verbose_name='Expired Quantity',
                                           help_text='Expired Quantity of the Item.')
