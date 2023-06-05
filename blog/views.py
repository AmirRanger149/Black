from .serializers import BlogPageSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import BlogPage


class BlogPageAPIView(APIView):
    def get(self, request, *args, **kwargs):
        posts = BlogPage.objects.all()
        serializer = BlogPageSerializer(posts, many=True)
        return Response(serializer.data)