from user.models  import User
from store.models import Store

from django.db              import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Pizza(models.Model):
    name_kr = models.CharField(max_length = 45, null = True)
    name_en = models.CharField(max_length = 45, null = True)
    image   = models.URLField(max_length = 500, null = True)

    class Meta:
        db_table = 'pizzas'

class Score(models.Model):
    user         = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    pizza        = models.ForeignKey('Pizza', on_delete = models.SET_NULL, null = True)
    store        = models.ForeignKey(Store, on_delete = models.SET_NULL, null = True)
    order_number = models.CharField(max_length = 200, null = True)
    time         = models.FloatField(null = True)
    quality      = models.IntegerField(validators = [MaxValueValidator(100), MinValueValidator(0)], null = True)
    sauce        = models.IntegerField(validators = [MaxValueValidator(100), MinValueValidator(0)], null = True)
    cheese       = models.IntegerField(validators = [MaxValueValidator(100), MinValueValidator(0)], null = True)
    topping      = models.IntegerField(validators = [MaxValueValidator(100), MinValueValidator(0)], null = True)
    created_at   = models.DateTimeField(auto_now_add = True)
    updated_at   = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'scores'
