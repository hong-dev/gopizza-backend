from .views import ScoreView, UserRankView, StoreRankView

from django.urls import path, include

urlpatterns = [
    path('', ScoreView.as_view()),
    path('/user', UserRankView.as_view()),
    path('/store', StoreRankView.as_view())
]
