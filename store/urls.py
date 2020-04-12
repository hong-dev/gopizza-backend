from .views import StoreListView, StoreDetailView
from django.urls import path

urlpatterns = [
    path('', StoreListView.as_view()),
    path('/detail/<int:store_id>', StoreDetailView.as_view()),
]
