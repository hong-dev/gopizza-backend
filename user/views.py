import json
import bcrypt
import jwt
import boto3
import uuid
from PIL import Image
from io  import BytesIO

from .models      import User, Grade, Verification
from store.models import Store
from my_settings  import SECRET, ALGORITHM, EMAIL, S3
from .texts       import message
from .tokens      import account_activation_token
from .utils       import login_required

from django.views                   import View
from django.http                    import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http              import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail               import EmailMessage
from django.utils.encoding          import force_bytes, force_text
from django.db.models               import Q

class EmailVerificationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = Verification.objects.create(
                email        = data['email'],
                is_activated = False,
            )

            current_site  = get_current_site(request)
            domain        = current_site.domain
            uidb64        = urlsafe_base64_encode(force_bytes(user.pk))
            token         = account_activation_token.make_token(user)
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
            uid  = force_text(urlsafe_base64_decode(uidb64))
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
            if Verification.objects.filter(email = data['email']).filter(is_activated = True):

                if User.objects.filter(email = data['email']).exists():

                    return JsonResponse({"message" : "DUPLICATED_EMAIL"}, status = 400)

                user_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
                User(
                    grade    = Grade.objects.get(id = data.get('grade', 3)),
                    store    = Store.objects.get(id = data.get('store', None)),
                    name     = data['name'],
                    email    = data['email'],
                    password = user_password.decode('utf-8'),
                    image    = data.get('image_url', None),
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

class UserListView(View):
    def get(self, request):
        users = [
            [{
                store : list(
                    User
                    .objects
                    .filter(store_id = store)
                    .values_list('id', flat = True)
                )
            } for store in list(
                Store
                .objects
                .values_list('id', flat = True)
            )],
            {
                "user_name" : list(
                    User
                    .objects
                    .values_list('name', flat = True)
                )
            }
        ]

        return JsonResponse({"users" : users}, status = 200)

class ProfileUploadView(View):
    s3_client = boto3.client(
        's3',
        aws_access_key_id     = S3['Access_Key_ID'],
        aws_secret_access_key = S3['Secret_Access_Key']
    )
    def post(self, request):
        try:
            image  = request.FILES['filename']
            im     = Image.open(image)
            im     = im.resize((400, 400))
            buffer = BytesIO()
            im.save(buffer, "JPEG")
            buffer.seek(0)

            url_generator = str(uuid.uuid4())
            self.s3_client.upload_fileobj(
                buffer,
                "wepizza",
                url_generator,
                ExtraArgs = {
                    "ContentType": "image/jpeg"
                }
            )
            image_url = f'{S3["Address"]}{url_generator}'

            return JsonResponse({"image_url" : image_url}, status = 200)

        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status = 400)

class UserGetView(View):
    @login_required
    def get(self, request):
        grade_id = request.user.grade_id
        store_id = request.user.store_id

        if grade_id == 3:
            return JsonResponse({"message" : "Forbidden"}, status = 403)

        filter_condition = {}
        if grade_id == 2:
            filter_condition = {'store_id' : store_id}

        users = (
            User
            .objects
            .filter(**filter_condition)
            .filter(~Q(grade_id = 1))
            .select_related('grade', 'store')
            .values(
                "id",
                "name",
                "grade_id",
                "grade__name",
                "is_approved",
                "store_id",
                "store__name"
            )
        )

        return JsonResponse({"user" : list(users)}, status = 200)

class UserDeleteView(View):
    @login_required
    def delete(self, request, user_id):
        User.objects.get(id = user_id).delete()
        return HttpResponse(status = 200)

