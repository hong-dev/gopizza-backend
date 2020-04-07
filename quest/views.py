from .models    import Quest, UserQuestHistory
from user.utils import login_required

from django.views import View
from django.http  import HttpResponse, JsonResponse

class QuestListView(View):
    @login_required
    def get(self, request):
        quest_list = list(
            UserQuestHistory
            .objects
            .select_related('quest')
            .filter(user_id = request.user.id)
            .values(
                'is_achieved',
                'is_claimed',
                'is_rewarded',
                'quest_id',
                'quest__name',
                'quest__goal',
                'quest__description'
            )
        )

        return JsonResponse({"quests" : quest_list}, status = 200)

class QuestClaimView(View):
    @login_required
    def post(self, request, quest_id):
        user_quest = UserQuestHistory.objects.get(
            quest_id = quest_id,
            user_id  = request.user.id
        )

        if user_quest.is_achieved:
            if user_quest.quest.badge:
                user_quest.is_claimed  = True
                user_quest.is_rewarded = True
                user_quest.save()

                return JsonResponse({"badge" : user_quest.quest.badge}, status = 200)

            user_quest.is_claimed = True
            user_quest.save()

            return JsonResponse({"message" : "Claim Succeed"}, status = 200)

        return JsonResponse({"ERROR" : "IS_NOT_ACHIEVED"}, status = 400)
