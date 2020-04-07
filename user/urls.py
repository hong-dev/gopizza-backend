from .views import (
    SignUpView,
    SignInView,
    EmailVerificationView,
    UserListView,
    ProfileUploadView,
    UserGetView,
    CheckPasswordView,
    UserDeleteView,
    PasswordChangeView,
    ImageChangeView
)


from django.urls import path

urlpatterns = [
    path('/sign-up', SignUpView.as_view()),
    path('/sign-in', SignInView.as_view()),
    path('/email-verification', EmailVerificationView.as_view()),
    path('/email-verification/<str:uidb64>/<str:token>', EmailVerificationView.as_view()),
    path('', UserListView.as_view()),
    path('/profile-upload', ProfileUploadView.as_view()),
    path('/get', UserGetView.as_view()),
    path('/check-password', CheckPasswordView.as_view()),
    path('/delete/<int:user_id>', UserDeleteView.as_view()),
    path('/password', PasswordChangeView.as_view()),
    path('/image', ImageChangeView.as_view())
]
