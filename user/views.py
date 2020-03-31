import json
import bcrypt
import jwt

from .models      import User, Grade, Verification
from store.models import Store
from my_settings  import SECRET, ALGORITHM, EMAIL
from .texts       import message
from .tokens      import account_activation_token

from django.views                   import View
from django.http                    import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http              import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail               import EmailMessage
from django.utils.encoding          import force_bytes, force_text

class EmailVerificationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = Verification.objects.create(
                email = data['email'],
                is_activated = False,
            )

            current_site = get_current_site(request)
            domain = current_site.domain
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            email_content = message(domain, uidb64, token)

            email_subject = "[GOPIZZA] 이메일 인증 안내"
            email_to      = data['email']
            email         = EmailMessage(email_subject, email_content, to = [email_to])
            email.send()

            return JsonResponse({"Message" : "Please Check Your Email!"}, status = 200)

        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status = 400)

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = Verification.objects.get(pk = uid)

            if account_activation_token.check_token(user, token):
                user.is_activated = True
                user.save()

                return JsonResponse({"message" : "Verification Succeed"}, status = 200)

            return JsonResponse({"message" : "Verification Failed"}, status = 401)

        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status = 400)

class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            if Verification.objects.filter(email = data['email']).exists():

                if User.objects.filter(email = data['email']).exists():
                    return JsonResponse({"message" : "DUPLICATED_EMAIL"}, status = 400)

                user_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
                User(
                    grade    = Grade.objects.get(id = data.get('grade', 3)),
                    store    = Store.objects.get(id = data.get('store', 46)),
                    name     = data['name'],
                    email    = data['email'],
                    password = user_password.decode('utf-8'),
                ).save()

                return HttpResponse(status = 200)

            return JsonResponse({"message" : "Need Email Verification"}, status = 403)

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
