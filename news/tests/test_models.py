from django.test import TestCase
from django.db import IntegrityError
from news.models import Tag, News



class TagModelTest(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name="Technology")
        self.tag2 = Tag.objects.create(name="Science")
    
    def test_tag_creation(self):
        """Test that a tag can be created"""
        self.assertEqual(self.tag1.name, "Technology")
    
    def test_tag_uniqueness(self):
        """Test that tag names must be unique"""
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Technology")


class NewsModelTest(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name="Technology")
        self.tag2 = Tag.objects.create(name="Science")
        
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
    
    def test_news_creation(self):
        """Test that news items can be created with tags"""
        self.assertEqual(self.news1.title, "Test News 1")
        self.assertEqual(self.news1.tags.count(), 1)
        self.assertEqual(self.news2.tags.count(), 2)
    
    def test_news_ordering(self):
        """Test that news items are ordered by created date (newest first)"""
        news_list = list(News.objects.all())
        self.assertEqual(news_list[0], self.news2)
    
    def test_news_source_uniqueness(self):
        """Test that news source URLs must be unique"""
        with self.assertRaises(IntegrityError):
            News.objects.create(
                title="Duplicate Source",
                content="This has a duplicate source",
                # Same as news1
                source="https://example.com/news1"  
            )
    
    def test_news_search_by_tags(self):
        """Test the search method with tags"""
        results = News.search(tags=["Technology"])
        self.assertEqual(results.count(), 2)
        
        results = News.search(tags=["Science"])
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.news2)
        
        results = News.search(tags=["Technology", "Science"])
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.news2)
    
    def test_news_search_by_keywords(self):
        """Test the search method with keywords"""
        results = News.search(kws=["test"])
        self.assertEqual(results.count(), 2)
        
        results = News.search(kws=["content 1"])
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.news1)
    
    def test_news_search_with_excluded_keywords(self):
        """Test the search method with excluded keywords"""
        results = News.search(not_kws=["content 1"])
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.news2)
    
    def test_news_search_combined(self):
        """Test the search method with combined parameters"""
        results = News.search(
            tags=["Technology"],
            kws=["test"],
            not_kws=["content 1"]
        )
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.news2)
