from .views import QuestListView
from django.urls import path

urlpatterns = [
    path('', QuestListView.as_view()),
]
