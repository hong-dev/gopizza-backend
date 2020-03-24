from django.db import models

class Store(models.Model):
    name          = models.CharField(max_length = 50)
    address       = models.CharField(max_length = 200, null = True)
    phone_number  = models.CharField(max_length = 50, null = True)
    longitude     = models.DecimalField(max_digits = 8, decimal_places = 5, null = True)
    latitude      = models.DecimalField(max_digits = 8, decimal_places = 5, null = True)
    created_at    = models.DateTimeField(auto_now_add = True)
    updated_at    = models.DateTimeField(auto_now = True)
    class Meta:
        db_table = 'stores'

