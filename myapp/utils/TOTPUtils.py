from datetime import timedelta

import pyotp
from django.utils import timezone

from ..models import OTP

TOTP_SECRET = 'P7V63FLDP2F5Y3OA2H4Z3XOVEKPUW6HA'
totp = pyotp.TOTP(TOTP_SECRET, interval=60)


def generate_otp():
    return totp.now()


def check_otp(otp):
    return totp.verify(otp)


def verify_otp(user_otp, email):
    print(check_otp(user_otp))
    if not OTP.objects.filter(key=email).exists():
        return 0
    otp_instance = OTP.objects.filter(key=email).order_by('-created_on').first()
    print(otp_instance.otp, user_otp)
    print(otp_instance.otp == user_otp)
    if otp_instance and (timezone.now() - otp_instance.created_on) < timedelta(minutes=10):
        if otp_instance.otp == user_otp:
            otp_instance.delete()
            return 1
    return 0
