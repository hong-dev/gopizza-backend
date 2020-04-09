from .views import (
    ScoreView,
    UserRankView,
    StoreRankView,
    PizzaView,
    UserScoreView
)

from django.urls import path, include

urlpatterns = [
    path('', ScoreView.as_view()),
    path('/pizza', PizzaView.as_view()),
    path('/user', UserRankView.as_view()),
    path('/store', StoreRankView.as_view()),
    path('/<int:user_id>', UserScoreView.as_view())
]
