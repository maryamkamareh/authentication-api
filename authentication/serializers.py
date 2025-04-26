from rest_framework import serializers
import re


class MobileSerializer(serializers.Serializer):
    mobile = serializers.CharField()

    def validate_mobile(self, value):
        if not re.match(r'^09\d{9}$', value):
            raise serializers.ValidationError("Invalid mobile number format.")
        return value


class PasswordLoginSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    password = serializers.CharField()


class OTPVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField()
    code = serializers.CharField()

    def validate_code(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("Invalid OTP code format.")
        return value


class CompleteProfileSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
