from rest_framework import serializers
from .models import BlogPage


class BlogPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogPage
        fields = ('id', 'title', 'owner', 'comments_count', 'image', 'collection', 'intro', 'date', 'body', 'description')
