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
