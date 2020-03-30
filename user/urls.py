from .views import SignUpView, SignInView, EmailVerificationView

from django.urls import path

urlpatterns = [
    path('/sign-up', SignUpView.as_view()),
    path('/sign-in', SignInView.as_view()),
    path('/email-verification', EmailVerificationView.as_view()),
    path('/email-verification/<str:uidb64>/<str:token>', EmailVerificationView.as_view()),
]
