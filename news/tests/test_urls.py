from django.test import TestCase
from django.urls import reverse, resolve
from rest_framework.test import APIClient
from rest_framework import status
from news.views import TagAPI, NewsAPI



class UrlsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_news_list_url(self):
        """Test that the news list URL resolves correctly"""
        url = reverse('news:news-list')
        self.assertEqual(url, '/news/')
        
        resolver = resolve(url)
        self.assertEqual(
            resolver.func.__name__,
            NewsAPI.as_view().__name__
        )
    
    def test_news_detail_url(self):
        """Test that the news detail URL resolves correctly"""
        url = reverse('news:news-detail', args=[1])
        self.assertEqual(url, '/news/1/')
        
        resolver = resolve(url)
        self.assertEqual(
            resolver.func.__name__,
            NewsAPI.as_view().__name__
        )

    def test_tag_list_url(self):
        """Test that the tag list URL resolves correctly"""
        url = reverse('news:tag-list')
        self.assertEqual(url, '/tags/')
        
        resolver = resolve(url)
        self.assertEqual(
            resolver.func.__name__,
            TagAPI.as_view().__name__
        )
    
    def test_tag_detail_url(self):
        """Test that the tag detail URL resolves correctly"""
        url = reverse('news:tag-detail', args=[1])
        self.assertEqual(url, '/tags/1/')
        
        resolver = resolve(url)
        self.assertEqual(
            resolver.func.__name__,
            TagAPI.as_view().__name__
        )
    
    def test_404_for_invalid_url(self):
        """Test that invalid URLs return 404"""
        response = self.client.get('/invalid-endpoint/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
