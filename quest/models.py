from user.models import User
from django.db   import models

class Category(models.Model):
    name = models.CharField(max_length = 50)

    class Meta:
        db_table = 'categories'

class Quest(models.Model):
    category    = models.ForeignKey(Category, on_delete = models.SET_NULL, null = True)
    name        = models.CharField(max_length = 50, null = True)
    goal        = models.IntegerField(null = True)
    description = models.CharField(max_length = 500, null = True)
    badge       = models.CharField(max_length = 300, null = True)
    reward      = models.CharField(max_length = 300, null = True)

    class Meta:
        db_table = 'quests'

class UserQuestHistory(models.Model):
    user        = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    quest       = models.ForeignKey(Quest, on_delete = models.SET_NULL, null = True)
    is_achieved = models.BooleanField(null = True)
    is_claimed  = models.BooleanField(null = True)
    is_rewarded = models.BooleanField(null = True)
    created_at  = models.DateTimeField(auto_now_add = True)
    updated_at  = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'user_quest_histories'
