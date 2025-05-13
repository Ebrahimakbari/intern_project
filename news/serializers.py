from rest_framework import serializers
from .models import Tag, News
from django.db import transaction


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

    def validate_name(self, value):
        value = value.strip()
        return value


class NewsSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True
    )
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'tags', 'tags_detail', 'source', 'created', 'updated']


    def validate_source(self, value):
        """
        Check if the source URL already exists in the database.
        If it does, raise a validation error.
        """
        # For update operations, exclude the current instance
        instance = getattr(self, 'instance', None)
        
        # If this is an update operation and the source hasn't changed, skip validation
        if instance and instance.source == value:
            return value
            
        # Check if another news item has this source
        if News.objects.filter(source=value).exists():
            raise serializers.ValidationError("A news item with this source URL already exists.")
            
        return value

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        news = News.objects.create(**validated_data)
        self._process_tags(news, tags_data)

        return news

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])

        # Update the news instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_data is not None:
            instance.tags.clear()
            self._process_tags(instance, tags_data)

        return instance

    def _process_tags(self, news, tags_data):
        """
        Process tags for a news item:
        - If a tag with the given name exists, use it
        - If not, create a new tag
        """
        for tag_data in tags_data:
            tag_name = tag_data.strip()
            if tag_name:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                # Add tag to news
                news.tags.add(tag)
