from .views import (
    ScoreView,
    UserRankView,
    StoreRankView,
    PizzaView,
    UserScoreView,
    StoreScoreView
)

from django.urls import path, include

urlpatterns = [
    path('', ScoreView.as_view()),
    path('/pizza', PizzaView.as_view()),
    path('/user', UserRankView.as_view()),
    path('/store', StoreRankView.as_view()),
    path('/user/<int:user_id>', UserScoreView.as_view()),
    path('/store/<int:store_id>', StoreScoreView.as_view())
]
