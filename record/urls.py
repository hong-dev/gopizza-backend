from .views import ScoreView

from django.urls import path, include

urlpatterns = [
    path('', ScoreView.as_view()),
]
