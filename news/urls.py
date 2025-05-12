from django.urls import path
from . import views


app_name = 'news'
urlpatterns = [
    path('list/', views.ListNewsAPI.as_view(), name='news_list'),
]
