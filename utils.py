from django.contrib.auth import get_user_model
from rest_framework import permissions
User = get_user_model()


class MyBackend:
    """
    Authentication based on phone_number and password.
    """
    def authenticate(phone_number=None, password=None):
        user = User.objects.filter(phone_number=phone_number)
        if user.exists() and user.first().check_password(password):
            return user.first()
        return None


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    permission to allow anyone to GET but only admins to POST, PUT, DELETE
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated and request.user.is_staff
