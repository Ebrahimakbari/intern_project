from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework.request import Request
from .serializers import NewsSerializer, TagSerializer
from .models import News, Tag
from django.shortcuts import get_object_or_404
from .pagination import PaginationMixin, CustomPagination


class NewsAPI(PaginationMixin, views.APIView):
    """
    API view to list, retrieve, update or delete a specific news item based on tags,
    keywords, and excluded keywords.
    """

    pagination_class = CustomPagination
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(News, pk=pk)

    def get(self, request: Request, pk=None, *args, **kwargs):
        if pk:
            # Retrieve a specific news item
            news = get_object_or_404(News, pk=pk)
            serializer = NewsSerializer(news)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # List news items with optional filtering
            tags = request.query_params.getlist('tags', '')
            kws = request.query_params.getlist('kws', '')
            not_kws = request.query_params.getlist('not_kws', '')
            query = News.search(tags, kws, not_kws)

            # Apply pagination
            page = self.paginate_queryset(query)
            if page is not None:
                serializer = NewsSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = NewsSerializer(query, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, *args, **kwargs):
        """Create a new news item"""
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                news = serializer.save()
                return Response(
                    NewsSerializer(news).data,
                    status=status.HTTP_201_CREATED
                )
            except:
                return Response(
                    {"error": f"Failed to create news"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request, pk, *args, **kwargs):
        """partially Update a specific news item"""
        news = self.get_object(pk)
        serializer = NewsSerializer(news, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                updated_news = serializer.save()
                return Response(
                    NewsSerializer(updated_news).data,
                    status=status.HTTP_200_OK
                )
            except:
                return Response(
                    {"error": f"Failed to update news"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk, *args, **kwargs):
        """Delete a specific news item"""
        news = self.get_object(pk)
        news.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagAPI(PaginationMixin, views.APIView):
    """
    API view to list, retrieve, update or delete tag items.
    """
    # permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request: Request, pk=None, *args, **kwargs):
        if pk:
            # Retrieve a specific tag
            tag = get_object_or_404(Tag, pk=pk)
            serializer = TagSerializer(tag)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            tags = Tag.objects.all()

            # Apply pagination
            page = self.paginate_queryset(tags)
            if page is not None:
                serializer = TagSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = TagSerializer(tags, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, *args, **kwargs):
        """Create a new tag"""
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            try:
                tag = serializer.save()
                return Response(
                    TagSerializer(tag).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"error": f"Failed to create tag: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request, pk, *args, **kwargs):
        """partially Update a specific tag"""
        tag = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                updated_tag = serializer.save()
                return Response(
                    TagSerializer(updated_tag).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"error": f"Failed to update tag: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk, *args, **kwargs):
        """Delete a specific tag"""
        tag = get_object_or_404(Tag, pk=pk)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
