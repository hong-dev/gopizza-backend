import json
import bcrypt
import jwt

from .models      import User, Grade
from store.models import Store
from my_settings  import SECRET, ALGORITHM

from django.views import View
from django.http  import HttpResponse, JsonResponse

class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            if User.objects.filter(email = data['email']).exists():
                return JsonResponse({"message" : "DUPLICATED_EMAIL"}, status = 400)

            user_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            User(
                grade    = Grade.objects.get(id = data.get('grade', 3)),
                store    = Store.objects.get(id = data.get('store', None)),
                name     = data['name'],
                email    = data['email'],
                password = user_password.decode('utf-8'),
            ).save()

            return HttpResponse(status = 200)

        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status = 400)

class SignInView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            if User.objects.filter(email = data['email']).exists():
                user = User.objects.get(email = data['email'])

                if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
                    token = jwt.encode({"user" : user.id}, SECRET['secret'], ALGORITHM)

                    return JsonResponse({"token" : token.decode('utf-8')}, status = 200)
                return HttpResponse(status = 401)
            return HttpResponse(status = 401)

        except  KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status = 400)
