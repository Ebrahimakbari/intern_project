from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)




app_name = 'account'
urlpatterns = [
    path('register/', views.UserRegisterViewAPI.as_view(), name='register_api'),
    path('users/login/', views.LoginUserAPI.as_view(), name='login_api'),
    path('users/logout/', views.LogoutUserAPI.as_view(), name='logout_api'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]