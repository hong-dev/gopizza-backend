from .views import StoreListView
from django.urls import path

urlpatterns = [
    path('', StoreListView.as_view()),
]
