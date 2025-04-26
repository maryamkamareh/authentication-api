from django.urls import path
from .views import *

urlpatterns = [
    path('request-otp/', RequestOTP.as_view()),
    path('verify-otp/', VerifyOTP.as_view()),
    path('complete-profile/', CompleteProfile.as_view()),
    path('password-login/', PasswordLogin.as_view()),
]
