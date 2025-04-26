from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login
from .models import User, OTP
from .serializers import *
from .utils import get_client_ip, block_check, increase_attempts, reset_attempts, generate_unique_otp


class RequestOTP(APIView):
    """درخواست ثبت موبایل و تعیین مسیر ثبت‌نام یا ورود"""

    def post(self, request):
        serializer = MobileSerializer(data=request.data)
        if serializer.is_valid():
            ip = get_client_ip(request)
            mobile = serializer.validated_data['mobile']
            if block_check(ip, mobile):
                return Response({"detail": "Blocked for one hour."}, status=status.HTTP_403_FORBIDDEN)
            # ✅ بررسی وجود کاربر
            if User.objects.filter(mobile=mobile).exists():
                return Response(
                    {"detail": "User already exists. Please login with password."},
                    status=status.HTTP_409_CONFLICT
                )
            # کاربر جدید
            code = generate_unique_otp()
            OTP.objects.create(mobile=mobile, code=code)
            # تولید کد 6 رقمی، شبیه ساز پیامک
            return Response({"detail": f"OTP code {code} generated."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):
    """تایید کد یکبار مصرف (OTP) و ایجاد حساب کاربری"""

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            ip = get_client_ip(request)
            mobile = serializer.validated_data['mobile']
            code = serializer.validated_data['code']
            try:
                otp = OTP.objects.filter(mobile=mobile).latest('created_at')
            except OTP.DoesNotExist:
                increase_attempts(ip, mobile)
                return Response({"detail": "OTP not found."}, status=status.HTTP_400_BAD_REQUEST)

            # بررسی انقضای 1 دقیقه‌ای
            expiration_time = otp.created_at + timedelta(minutes=1)
            if timezone.now() > expiration_time:
                increase_attempts(ip, mobile)
                return Response({"detail": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)
            if otp.code != code:
                increase_attempts(ip, mobile)
                return Response({"detail": "Wrong OTP."}, status=status.HTTP_400_BAD_REQUEST)
            user, created = User.objects.get_or_create(mobile=mobile)
            if created:
                # برای کاربر جدید رمز اولیه می‌توانیم ست کنیم یا جدا از کاربر رمز بگیریم
                user.set_password("temporary_password")
                user.save()
            reset_attempts(ip, mobile)
            return Response({"detail": "Verified successfully. Complete your profile."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteProfile(APIView):
    """تکمیل اطلاعات پروفایل بعد از تایید OTP"""

    def post(self, request):
        serializer = CompleteProfileSerializer(data=request.data)
        if serializer.is_valid():
            # به طور موقت کاربر را از طریق موبایل واکشی می‌کنیم
            mobile = request.data.get('mobile')
            try:
                user = User.objects.get(mobile=mobile)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            user.first_name = serializer.validated_data['first_name']
            user.last_name = serializer.validated_data['last_name']
            user.email = serializer.validated_data['email']
            user.save()
            return Response({"detail": "Profile completed."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordLogin(APIView):
    """ورود کاربر با شماره موبایل و رمز عبور"""

    def post(self, request):
        serializer = PasswordLoginSerializer(data=request.data)
        if serializer.is_valid():
            ip = get_client_ip(request)
            mobile = serializer.validated_data['mobile']
            password = serializer.validated_data['password']
            if block_check(ip, mobile):
                return Response({"detail": "Blocked for one hour."}, status=status.HTTP_403_FORBIDDEN)
            user = authenticate(mobile=mobile, password=password)
            if user is not None:
                reset_attempts(ip, mobile)
                login(request, user)
                return Response({"detail": "Logged in successfully."})
            else:
                increase_attempts(ip, mobile)
                return Response({"detail": "Wrong credentials."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
