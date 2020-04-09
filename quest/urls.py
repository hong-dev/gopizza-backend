from .views import (
    QuestListView,
    QuestClaimView,
    ScoreGetView,
    RewardAprrovalView
)
from django.urls import path

urlpatterns = [
    path('', QuestListView.as_view()),
    path('/claim/<int:quest_id>', QuestClaimView.as_view()),
    path('/get-my-score', ScoreGetView.as_view()),
    path('/reward-approval', RewardAprrovalView.as_view()),
    path('/reward-approval/user/<int:user__id>/quest/<int:quest__id>', RewardAprrovalView.as_view()),
]
