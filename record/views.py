import json

from .models     import Score, Pizza
from user.models import User

from django.views     import View
from django.http      import HttpResponse, JsonResponse

class ScoreView(View):
    def post(self, request):
        try:
            score_data = json.loads(request.body)
            Score.objects.create(
                order_number = score_data["order_number"],
                user         = User.objects.get(id = score_data["user_id"]),
                pizza        = Pizza.objects.get(id = score_data["score"]["pizza_id"]),
                time         = score_data["score"]["time"],
                quality      = score_data["score"]["quality"],
                sauce        = score_data["score"]["sauce"],
                cheese       = score_data["score"]["cheese"],
                topping      = score_data["score"]["topping"]
            )
            return HttpResponse(status = 200)

        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status = 400)
