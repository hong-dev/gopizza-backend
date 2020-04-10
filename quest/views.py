from .models     import Quest, UserQuestHistory
from user.models import User
from user.utils  import login_required
from my_settings import EMAIL

from django.views     import View
from django.http      import HttpResponse, JsonResponse
from django.db.models import Count
from django.core.mail import EmailMessage

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
                'quest__category__name',
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
                user_quest.save()

                return JsonResponse({"badge" : user_quest.quest.badge}, status = 200)

            user_quest.is_claimed = True
            user_quest.save()

            return JsonResponse({"coupon" : user_quest.quest.reward}, status = 200)

        return JsonResponse({"ERROR" : "IS_NOT_ACHIEVED"}, status = 400)

class ScoreGetView(View):
    @login_required
    def post(self, request):
        user_id = request.user.id
        total_counts = (
            User
            .objects
            .filter(id = user_id)
            .annotate(
                count = Count('score')
            )
            .values('count')
        )
        total_count = [count['count'] for count in total_counts ]

        sweet_potato_counts = (
            User
            .objects
            .filter(id = user_id)
            .filter(score__pizza_id = 7)
            .annotate(
                count = Count('score')
            )
            .values('count')
        )
        sweet_potato_count = [count['count'] for count in sweet_potato_counts]

        pepperoni_counts = (
            User
            .objects
            .filter(id = user_id)
            .filter(score__pizza_id = 4)
            .annotate(
                count = Count('score')
            )
            .values('count')
        )
        pepperoni_count = [count['count'] for count in pepperoni_counts]

        if total_count == []:
            total_count = 0
        else :
            total_count = total_count[0]

        if sweet_potato_count == []:
            sweet_potato_count = 0
        else:
            sweet_potato_count = sweet_potato_count[0]

        if pepperoni_count == []:
            pepperoni_count = 0
        else:
            pepperoni_count = pepperoni_count[0]

        pizza_counts = {
            'total'        : total_count,
            'sweet_potato' : sweet_potato_count,
            'pepperoni'    : pepperoni_count
        }

        quest_1 = UserQuestHistory.objects.get(user_id = user_id, quest_id = 1)
        quest_2 = UserQuestHistory.objects.get(user_id = user_id, quest_id = 2)
        quest_3 = UserQuestHistory.objects.get(user_id = user_id, quest_id = 3)
        quest_4 = UserQuestHistory.objects.get(user_id = user_id, quest_id = 4)
        quest_5 = UserQuestHistory.objects.get(user_id = user_id, quest_id = 5)

        if quest_1.quest.goal <= total_count:
            quest_1.is_achieved = True
            quest_1.save()

        if quest_2.quest.goal <= total_count:
            quest_2.is_achieved = True
            quest_2.save()

        if quest_3.quest.goal <= total_count:
            quest_3.is_achieved = True
            quest_3.save()

        if quest_4.quest.goal <= sweet_potato_count:
            quest_4.is_achieved = True
            quest_4.save()

        if quest_5.quest.goal <= pepperoni_count:
            quest_5.is_achieved = True
            quest_5.save()

        return JsonResponse({"pizza_counts" : pizza_counts}, status = 200)

class RewardAprrovalView(View):
    @login_required
    def get(self, request):
        user_grade = request.user.grade.id
        if user_grade == 1:
            approvals = (
                UserQuestHistory
                .objects
                .filter(is_claimed = True)
                .order_by('is_rewarded')
                .values(
                    'user__id'
                    ,'user__name'
                    ,'user__store__name'
                    ,'quest__id'
                    ,'quest__name'
                    ,'updated_at'
                    ,'is_rewarded'
                )
            )
            approval_list = [ approval for approval in approvals ]

            return JsonResponse({"approval_list" : approval_list}, status = 200)

        return JsonResponse({"message" : "Access Denied"}, status = 403)

    @login_required
    def post(self, request, user__id, quest__id):
        user_grade = request.user.grade.id
        if user_grade == 1:
            user_quest = UserQuestHistory.objects.get(
                user_id  = user__id,
                quest_id = quest__id
            )

            if user_quest.is_claimed:
                if user_quest.quest.badge:
                    user_quest.is_rewarded  = True
                    user_quest.save()

                    email_subject = "[GOPIZZA] 리워드 지급 안내"
                    email_to      = user_quest.user.email
                    email         = EmailMessage(email_subject,'뱃지 지급이 완료되었습니다.', to = [email_to])
                    email.send()

                    return JsonResponse({"badge" : user_quest.quest.badge}, status = 200)

                user_quest.is_rewarded = True
                user_quest.save()

                email_subject = "[GOPIZZA] 리워드 지급 안내"
                email_to      = user_quest.user.email
                email         = EmailMessage(email_subject, '쿠폰 지급이 완료되었습니다.' ,to = [email_to])
                email.send()

                return JsonResponse({"coupon" : user_quest.quest.reward}, status = 200)

            return JsonResponse({"ERROR" : "IS_NOT_CLAIMED"}, status = 400) 

        return JsonResponse({"message" : "Access Denied"}, status = 403)

class BadgeCouponView(View):
    def get(self, request, user_id):
        quest_history = (
            UserQuestHistory
            .objects
            .select_related('quest', 'user')
            .filter(user_id = user_id)
        )

        coupon = [
            {
                "name"        : quest.quest.name,
                "is_rewarded" : quest.is_rewarded,
                "image"       : quest.quest.reward
            } for quest in quest_history if quest.quest.reward]

        badge = [
            {
                "name"        : quest.quest.name,
                "is_rewarded" : quest.is_rewarded,
                "image"       : quest.quest.badge
            } for quest in quest_history if quest.quest.badge]

        reward = {
            "coupon_count" : (
                quest_history
                .filter(is_rewarded = True)
                .exclude(quest__reward = '')
                .count()
            ),
            "badge_count"  : (
                quest_history
                .filter(is_rewarded = True)
                .exclude(quest__badge = '')
                .count()
            )
        }

        return JsonResponse({"coupon" : coupon, "badge" : badge, "reward" : reward}, status = 200)
