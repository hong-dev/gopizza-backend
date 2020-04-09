import json
import bcrypt
import jwt
import boto3
import uuid
import random
import string
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
                "image",
                "grade_id",
                "grade__name",
                "is_approved",
                "store_id",
                "store__name"
            )
        )

        return JsonResponse({"user" : list(users)}, status = 200)

class CheckPasswordView(View):
    @login_required
    def post(self, request):
        user = request.user
        data = json.loads(request.body)

        if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
            return JsonResponse({"user_id" : user.id}, status = 200)

        return JsonResponse({"message" : "WRONG_PASSWORD"}, status = 400)

class UserDeleteView(View):
    @login_required
    def delete(self, request, user_id):
        User.objects.get(id = user_id).delete()

        return HttpResponse(status = 200)

class PasswordChangeView(View):
    @login_required
    def post(self, request):
        user = request.user
        data = json.loads(request.body)

        password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        User.objects.filter(id = user.id).update(password = password.decode())

        return HttpResponse(status = 200)

class ImageChangeView(View):
    @login_required
    def post(self, request):
        user = request.user
        data = json.loads(request.body)

        User.objects.filter(id = user.id).update(image = data['image_url'])

        return HttpResponse(status = 200)

class UserInfoView(View):
    @login_required
    def get(self, request):
        user_id = request.user.id
        user_info = (
            User
            .objects
            .select_related('store')
            .filter(id = user_id)
            .values(
                "id",
                "name",
                "email",
                "store__name",
                "image"
            )
        )

        return JsonResponse({"user_info" : list(user_info)}, status = 200)

class ApprovalView(View):
    @login_required
    def post(self, request, user_id):
        grade_id = request.user.grade_id

        if grade_id == 3:
            return JsonResponse({"message" : "Forbidden"}, status = 403)

        User.objects.filter(id = user_id).update(is_approved = True)

        return HttpResponse(status = 200)

class NewPasswordView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data['email']

            digit = 10
            string_pool     = string.ascii_letters + string.digits 
            new_password    = ''.join(random.choice(string_pool) for x in range(digit))
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            user          = User.objects.get(email = email)
            user.password = hashed_password.decode('utf-8')
            user.save()

            email_subject = "[GOPIZZA] 임시 비밀번호 발급 안내"
            email_to      = data['email']
            email         = EmailMessage(
                email_subject,
                f" 임시비밀번호: {new_password} 
                \n 로그인 후 새로운 비밀번호로 변경 해주세요.",
                to = [email_to]
            )
            email.send()

            return JsonResponse({"Message" : "Password Reissued!"}, status = 200)
        except User.DoesNotExist :
            return JsonResponse({"Message" : "USER_DOES_NOT_EXIST"}, status = 400)


