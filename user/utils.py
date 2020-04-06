import jwt

from .models     import User
from my_settings import SECRET, ALGORITHM

from django.http import JsonResponse

def login_required(function):
    def wrapper(self, request, *args, **kwargs):
        token = request.headers.get('Authorization', None)

        if token:
            try:
                decode       = jwt.decode(token, SECRET['secret'], algorithms = ALGORITHM)
                user_info    = decode.get('user', None)
                user         = User.objects.get(id = user_info)
                request.user = user

            except jwt.DecodeError:
                return JsonResponse({"message" : "INVALID_TOKEN"}, status = 403)

            return function(self, request, *args, **kwargs)

        return JsonResponse({"message" : "LOGIN_REQUIRED"}, status = 401)
    return wrapper
