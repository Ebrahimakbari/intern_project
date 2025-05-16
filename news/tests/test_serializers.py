from django.test import TestCase
from news.models import News, Tag
from news.serializers import NewsSerializer, TagSerializer



class TagSerializerTest(TestCase):
    def setUp(self):
        self.tag_data = {"name": "Technology"}
        self.tag = Tag.objects.create(name="Science")
    
    def test_tag_serializer_create(self):
        """Test creating a tag with the serializer"""
        serializer = TagSerializer(data=self.tag_data)
        self.assertTrue(serializer.is_valid())
        tag = serializer.save()
        self.assertEqual(tag.name, "Technology")
    
    def test_tag_serializer_validation(self):
        """Test tag name validation"""
        # Test with existing tag name
        data = {"name": "Science"}
        serializer = TagSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        # Test with whitespace
        data = {"name": "  technology  "}
        serializer = TagSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        tag = serializer.save()
        self.assertEqual(tag.name, "technology")
    
    def test_tag_serializer_update(self):
        """Test updating a tag with the serializer"""
        serializer = TagSerializer(self.tag, data={"name": "physics"})
        self.assertTrue(serializer.is_valid())
        updated_tag = serializer.save()
        self.assertEqual(updated_tag.name, "physics")

class NewsSerializerTest(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name="Technology")
        self.tag2 = Tag.objects.create(name="Science")
        
        self.news = News.objects.create(
            title="Test News",
            content="This is test content",
            source="https://example.com/news"
        )
        self.news.tags.add(self.tag1)
        
        self.valid_data = {
            "title": "New News",
            "content": "This is new content",
            "source": "https://example.com/new",
            "tags": ["Technology", "Politics"]
        }
        
        self.invalid_data = {
            "title": "Duplicate Source",
            "content": "This has a duplicate source",
            # Same as self.news
            "source": "https://example.com/news",  
            "tags": ["Technology"]
        }

    def test_news_serializer_create(self):
        """Test creating news with the serializer"""
        serializer = NewsSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        news = serializer.save()
        self.assertEqual(news.title, "New News")
        self.assertEqual(news.tags.count(), 2)

    def test_news_serializer_validation(self):
        """Test news validation"""
        serializer = NewsSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('source', serializer.errors)
        
    def test_news_serializer_update(self):
        """Test updating news with the serializer"""
        update_data = {
            "title": "Updated Title",
            "tags": ["Science", "Health"]
        }
        
        serializer = NewsSerializer(self.news, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_news = serializer.save()
        
        self.assertEqual(updated_news.title, "Updated Title")
        self.assertEqual(updated_news.content, "This is test content")
        self.assertEqual(updated_news.tags.count(), 2)
        
        # Check that tags were updated
        self.assertIn(self.tag2, updated_news.tags.all())
