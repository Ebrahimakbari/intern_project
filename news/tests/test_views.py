from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from news.models import News, Tag
import json



class NewsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create tags
        self.tag1 = Tag.objects.create(name="technology")
        self.tag2 = Tag.objects.create(name="science")
        
        # Create news items
        self.news1 = News.objects.create(
            title="Test News 1",
            content="This is test content 1",
            source="https://example.com/news1"
        )
        self.news1.tags.add(self.tag1)
        
        self.news2 = News.objects.create(
            title="Test News 2",
            content="This is test content 2",
            source="https://example.com/news2"
        )
        self.news2.tags.add(self.tag1, self.tag2)
    
    def test_get_all_news(self):
        """Test retrieving all news items"""
        response = self.client.get(reverse('news:news-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check pagination
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)

    def test_get_news_detail(self):
        """Test retrieving a specific news item"""
        response = self.client.get(reverse('news:news-detail', args=[self.news1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test News 1')
    
    def test_create_news(self):
        """Test creating a news item"""
        data = {
            "title": "New News",
            "content": "This is new content",
            "source": "https://example.com/new",
            "tags": ["technology", "politics"]
        }
        
        response = self.client.post(
            reverse('news:news-list'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(News.objects.count(), 3)
        
        # Check that the tags were handled correctly
        new_news = News.objects.get(title="New News")
        self.assertEqual(new_news.tags.count(), 2)
        self.assertTrue(Tag.objects.filter(name="politics").exists())
    
    def test_update_news(self):
        """Test updating a news item"""
        data = {
            "title": "Updated Title",
            "tags": ["science", "health"]
        }
        
        response = self.client.put(
            reverse('news:news-detail', args=[self.news1.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.news1.refresh_from_db()
        self.assertEqual(self.news1.title, "Updated Title")
        self.assertEqual(self.news1.tags.count(), 2)
        self.assertTrue(Tag.objects.filter(name="health").exists())
    
    def test_delete_news(self):
        """Test deleting a news item"""
        response = self.client.delete(reverse('news:news-detail', args=[self.news1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(News.objects.count(), 1)
    
    def test_search_news(self):
        """Test searching news items"""
        # Search by tag
        response = self.client.get(f"{reverse('news:news-list')}?tags=science")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Search by keyword
        response = self.client.get(f"{reverse('news:news-list')}?kws=content 1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Search with excluded keyword
        response = self.client.get(f"{reverse('news:news-list')}?not_kws=content 1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Combined search
        response = self.client.get(
            f"{reverse('news:news-list')}?tags=technology&kws=test&not_kws=content 1"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class TagAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create tags
        self.tag1 = Tag.objects.create(name="technology")
        self.tag2 = Tag.objects.create(name="science")
        
        # Create a news item with tags
        self.news = News.objects.create(
            title="Test News",
            content="This is test content",
            source="https://example.com/news"
        )
        self.news.tags.add(self.tag1, self.tag2)
    
    def test_get_all_tags(self):
        """Test retrieving all tags"""
        response = self.client.get(reverse('news:tag-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_get_tag_detail(self):
        """Test retrieving a specific tag"""
        response = self.client.get(reverse('news:tag-detail', args=[self.tag1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'technology')
    
    def test_create_tag(self):
        """Test creating a tag"""
        data = {"name": "politics"}
        
        response = self.client.post(
            reverse('news:tag-list'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 3)
        self.assertTrue(Tag.objects.filter(name="politics").exists())
    
    def test_create_duplicate_tag(self):
        """Test creating a tag with a name that already exists"""
        data = {"name": "technology"}
        
        response = self.client.post(
            reverse('news:tag-list'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Tag.objects.count(), 2)
        
    def test_update_tag(self):
        """Test updating a tag"""
        data = {"name": "computer science"}
        
        response = self.client.put(
            reverse('news:tag-detail',
            args=[self.tag2.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.tag2.refresh_from_db()
        self.assertEqual(self.tag2.name, "computer science")
    
    def test_delete_tag(self):
        """Test deleting a tag"""
        response = self.client.delete(reverse('news:tag-detail', args=[self.tag1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objects.count(), 1)