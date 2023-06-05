from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from blog.serializers import BlogPageSerializer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from .models import BlogPage


def blog_post_list(request):
    
    if request.method == 'GET':
        blog_page = BlogPage.objects.all()
        serializer = BlogPageSerializer(blog_page, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return Response(status=404)