from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.request import Request
from .serializers import NewsSerializer
from .models import News





class ListNewsAPI(views.APIView):
    """
    API view to list news items based on tags, keywords, and excluded keywords.
    """
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request:Request, *args, **kwargs):
        tags = request.query_params.getlist('tags', '')
        kws = request.query_params.getlist('kws', '')
        not_kws = request.query_params.getlist('not_kws', '')
        query = News.search(tags, kws, not_kws)
        srz_data = NewsSerializer(query, many=True)
        return Response(data=srz_data.data, status=status.HTTP_200_OK)
