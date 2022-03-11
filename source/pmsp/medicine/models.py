import os

from accounts.models import Vendor, Customer
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, validate_image_file_extension
from django.db import models


def validate_jpeg_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Only jpeg files are accepted.')


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT / medicine_pk
    return 'medicine/images/medicine_{0}.jpeg'.format(instance.pk)


# Create your models here.
class Medicine(models.Model):
    image = models.ImageField(default=None, null=True, blank=True, upload_to=user_directory_path,
                              validators=[validate_image_file_extension, validate_jpeg_extension])
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    cost_price = models.DecimalField(decimal_places=2, max_digits=19, validators=[MinValueValidator(0.0)],
                                     verbose_name='Cost Price',
                                     help_text='Cost Price of the Medicine offered by the Vendor.')
    trade_name = models.CharField(unique=True, max_length=500, verbose_name='Trade Name',
                                  help_text='Common Name or Market Name of the Medicine.')
    scientific_name = models.CharField(max_length=500, verbose_name='Scientific Name',
                                       help_text='Scientific Name of the Medicine')
    description = models.TextField(verbose_name='Description', help_text='Description of the Medicine.')
    selling_price = models.DecimalField(decimal_places=2, max_digits=19, validators=[MinValueValidator(0.0)],
                                        verbose_name='Selling Price',
                                        help_text='Selling Price of the Medicine')

    def __str__(self):
        return self.trade_name

    @property
    def avg_rating(self):
        all_ratings = Rate.objects.filter(medicine_id=self.id).values_list('rating')
        if not all_ratings:
            return 0
        else:
            total = 0
            for rating in all_ratings:
                total += rating[0]
            return round(total / len(all_ratings), 2)


class Rate(models.Model):
    RATE_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )

    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    medicine_id = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    rate_date_time = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(choices=RATE_CHOICES, default=0, verbose_name='Rating by the User',
                                 help_text='Choose an appropriate rating for the medicine')

    class Meta:
        unique_together = (("medicine_id", "customer_id"),)
        verbose_name = 'Rate'
        verbose_name_plural = 'Rates'

    def __str__(self):
        return str(self.customer_id) + '---' + str(self.medicine_id) + '---' + str(self.rating) + ' stars'
