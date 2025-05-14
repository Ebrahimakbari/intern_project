from django.urls import path
from . import views


app_name = 'news'
urlpatterns = [
    # News endpoints
    path('news/', views.NewsAPI.as_view(), name='news-list'),
    path('news/<int:pk>/', views.NewsAPI.as_view(), name='news-detail'),
    
    # Tag endpoints
    path('tags/', views.TagAPI.as_view(), name='tag-list'),
    path('tags/<int:pk>/', views.TagAPI.as_view(), name='tag-detail'),
]
