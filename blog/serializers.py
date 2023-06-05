from wagtail.images.api.fields import ImageRenditionField
from rest_framework import serializers
from .models import BlogPage


class BlogPageSerializer(serializers.ModelSerializer):
    image = ImageRenditionField('fill-300x300')
    
    class Meta:
        model = BlogPage
        fields = ['id', 'comments', 'owner', 'image', 'collection', 'intro', 'date', 'body', 'description']
