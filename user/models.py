from store.models           import Store

from django.db              import models
from django.core.validators import MaxValueValidator, MinValueValidator

class User(models.Model):
    grade        = models.ForeignKey('Grade', on_delete = models.SET_NULL, null = True)
    store        = models.ForeignKey(Store, on_delete = models.SET_NULL, null = True)
    name         = models.CharField(max_length = 50, null = True)
    email        = models.CharField(max_length = 200, null = True)
    password     = models.CharField(max_length = 300)
    image        = models.CharField(max_length = 500, null = True)
    is_approved  = models.BooleanField(null = True)
    created_at   = models.DateTimeField(auto_now_add = True)
    updated_at   = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'users'

class Grade(models.Model):
    name = models.CharField(max_length = 50, null = True)

    class Meta:
        db_table = 'grades'

class Feedback(models.Model):
    user  = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    score = models.IntegerField(
        validators = [MaxValueValidator(10), MinValueValidator(1)], null = True
    )

    class Meta:
        db_table = 'feedbacks'

class Varification(models.Model):
    email        = models.CharField(max_length = 100)
    is_activated = models.BooleanField(null = True)
    created_at   = models.DateTimeField(auto_now_add = True)
    updated_at   = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'varifications'
