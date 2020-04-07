from .views import QuestListView, QuestClaimView, ScoreGetView
from django.urls import path

urlpatterns = [
    path('', QuestListView.as_view()),
    path('/claim/<int:quest_id>', QuestClaimView.as_view()),
    path('/get-my-score', ScoreGetView.as_view()),
]
