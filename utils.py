from django.contrib.auth import get_user_model

User = get_user_model()


class MyBackend:
    def authenticate(phone_number=None, password=None):
        user = User.objects.filter(phone_number=phone_number)
        if user.exists() and user.first().check_password(password):
            return user.first()
        return None