from authentication.models import LoginAttempt, OTP
from django.utils import timezone
import random


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_unique_otp():
    """Generate a 6-digit unique OTP"""
    while True:
        code = f"{random.randint(100000, 999999)}"
        if not OTP.objects.filter(code=code).exists():
            return code


def block_check(ip, mobile=None):
    attempts = LoginAttempt.objects.filter(ip_address=ip)
    if mobile:
        attempts = attempts.filter(mobile=mobile)
    for attempt in attempts:
        if attempt.blocked_until and timezone.now() < attempt.blocked_until:
            return True
    return False


def increase_attempts(ip, mobile=None):
    """Increase login/register failure attempts"""

    # افزایش شمارش بر اساس IP
    ip_obj, _ = LoginAttempt.objects.get_or_create(ip_address=ip, mobile=None)
    ip_obj.attempts += 1
    if ip_obj.attempts >= 3:
        ip_obj.blocked_until = timezone.now() + timezone.timedelta(hours=1)
        ip_obj.attempts = 0  # ریست شمارش بعد از بلاک
    ip_obj.save()

    # افزایش شمارش بر اساس Mobile
    if mobile:
        mobile_obj, _ = LoginAttempt.objects.get_or_create(ip_address=ip, mobile=mobile)
        mobile_obj.attempts += 1
        if mobile_obj.attempts >= 3:
            mobile_obj.blocked_until = timezone.now() + timezone.timedelta(hours=1)
            mobile_obj.attempts = 0
        mobile_obj.save()


def reset_attempts(ip, mobile=None):
    """Reset failure attempts after successful authentication"""

    LoginAttempt.objects.filter(ip_address=ip, mobile=mobile).delete()
