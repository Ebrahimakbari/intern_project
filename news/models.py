from django.db import models
from django.db.models import Q




class Tag(models.Model):
    """
    Tag model representing a tag item with name.
    """
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = ("Tag")
        verbose_name_plural = ("Tags")

    def __str__(self):
        return self.name


class News(models.Model):
    """
    News model representing a news item with title, content, tags, source, and timestamps.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='news_items')
    source = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name = ("news")
        verbose_name_plural = ("all news")

    def __str__(self):
        return self.title

    @classmethod
    def search(cls, tags=None, kws=None, not_kws=None):
        """
        Search for news items based on tags, keywords, and excluded keywords.
        """
        query = cls.objects.all()
        q_object = Q()
        if tags:
            for tag in tags:
                query = query.filter(tags__name=tag).distinct()
        if kws:
            for kw in kws:
                q_object |= Q(title__icontains=kw) | Q(content__contains=kw)
            query = query.filter(q_object)
        if not_kws:
            for not_kw in not_kws:
                q_object |= Q(title__icontains=not_kw) | Q(content__contains=not_kw)
            query = query.exclude(q_object)
        return query