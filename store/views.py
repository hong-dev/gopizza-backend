from .models import Store

from django.views import View
from django.http  import HttpResponse, JsonResponse

class StoreListView(View):
    def get(self, request):
        stores = Store.objects.values()
        store_list = [
            {
                "id"   : store['id'],
                "name" : store['name']
            } for store in stores ]

        return JsonResponse({"store_list" : store_list}, status = 200)
