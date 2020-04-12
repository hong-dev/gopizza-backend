from .models      import Store
from user.models  import User
from quest.models import UserQuestHistory

from django.views import View
from django.http  import HttpResponse, JsonResponse

class StoreListView(View):
    def get(self, request):
        stores = Store.objects.values()
        store_list = [
            {
                "id"        : store['id'],
                "name"      : store['name'],
                "address"   : store['address'],
                "latitude"  : store['latitude'],
                "longitude" : store['longitude']
            } for store in stores ]

        return JsonResponse({"store_list" : store_list}, status = 200)

class StoreDetailView(View):
    def get(self, request, store_id):
        crews = (
            User
            .objects
            .filter(store_id = store_id)
            .values()
        )
        crew_list = [
            {
                "id"     : crew['id'],
                "name"   : crew['name'],
                "image"  : crew['image'],
                "badge"  : [quest.quest.badge for quest in UserQuestHistory.objects.filter(user__id = crew['id']) if quest.is_claimed and quest.quest.badge ],
                "coupon" : [quest.quest.reward for quest in UserQuestHistory.objects.filter(user__id = crew['id']) if quest.is_claimed and quest.quest.reward],
            } for crew in crews ]

        return JsonResponse({"crew_list" : crew_list}, status = 200)
