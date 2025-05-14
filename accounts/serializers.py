from rest_framework import serializers, status
from accounts.models import CustomUser
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from utils import MyBackend
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'password',
                    'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data.keys():
            validated_data['password'] = make_password(
                validated_data['password'])
        return super().update(instance, validated_data)


class LoginUserSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data['phone_number']
        password = data['password']
        user = MyBackend.authenticate(
            phone_number=phone_number, password=password)
        if not user:
            raise AuthenticationFailed(
                'invalid credential!!', code=status.HTTP_400_BAD_REQUEST)
        data['tokens'] = user.get_token()
        data['user-info'] = {
            'phone_number': str(user.phone_number),
            'first_name': str(user.first_name),
            'last_name': str(user.last_name),
            'email': str(user.email),
        }
        return data


class LogoutUserSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, data):
        try:
            RefreshToken(data['refresh']).blacklist()
        except TokenError:
            raise ValidationError(
                'bad token!', code=status.HTTP_400_BAD_REQUEST)
        return data