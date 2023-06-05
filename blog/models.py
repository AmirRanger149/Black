"""
2020 Black
developer : #ABS
"""

# Import all requirements
from index.extensions.jalali_converter import jalali_converter as jConvert
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.images.api.fields import ImageRenditionField
from user_accounts.models import user_accounts as User
from django.views.decorators.csrf import csrf_exempt
from wagtail.snippets.models import register_snippet
from django.http import HttpRequest, JsonResponse
from rest_framework.renderers import JSONRenderer
from wagtail.api.v2.views import PagesAPIViewSet
from django.shortcuts import render, redirect
from wagtail.models import Page, PageManager
from wagtail.admin.panels import FieldPanel
from taggit.models import TaggedItemBase
from wagtail.fields import RichTextField
from rest_framework.fields import Field
from django.utils import timezone
from index.models import Comments
from wagtail.api import APIField
from wagtail.search import index
from django.db import models


# Blog Page Manager
class BlogPageManager(PageManager):
    ''' 
    DEVELOPMENT BY #ABS 
    '''
    pass


# Blog Index Child Serializer
class BlogPageChildSerializer(Field):
    ''' Serialize model => API | JSON '''
    def to_representation(self, value):
        return [
            {
                'id' : child.id,
                'slug' : child.slug,
                'comments' : child.comments,
                'title' : child.title,
                'intro' : child.intro,
                'author' : child.author,
                'image' : child.image,
                'date' : child.date,
                'description' : child.description,
                'collection' : child.collection,

            }for child in value
        ]


# blog app index model
class BlogIndex(Page, RoutablePageMixin):
    intro = RichTextField(blank=True, verbose_name='نام صفحه وبلاگ سایت')
    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
    max_count = 1
    objects = BlogPageManager()
    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    subpage_types = ['blog.BlogPage']

    parent_page_types = ['index.Index']

    def get_template(self, request, *args, **kwargs):

        return 'blog/blogarchive/blogarchive.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        loaded_post = BlogPage.objects.live().public().order_by('-first_published_at')
        context['posts'] = loaded_post if loaded_post is not None else 0
        return context

    def serve(self, request, *args, **kwargs):
        return render(
            request,
            self.get_template(request, *args, **kwargs),
            self.get_context(request, *args, **kwargs),
        )

    class Meta:
        verbose_name = 'صفحه اصلی وبلاگ'


# blog page model
class BlogPage(Page, RoutablePageMixin):
    comments = models.ManyToManyField('index.Comments', blank=True)
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL,)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='تصویر شاخص پست',
        help_text='یک تصویر بارگزاری کنید',
        )
    collection = models.ForeignKey(
        'index.categories',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='یک مجموعه انتخاب کنید',
    )
    intro = models.CharField(max_length=25, verbose_name='توضیحات ابتدایی راجب پست')
    date = models.DateTimeField("Post date",default=timezone.now)
    body = RichTextField(blank=True, verbose_name='محتوای پست')
    description = models.CharField(max_length=60, verbose_name='توضیحات کامل پست')

    subpage_types = []

    parent_page_types = ['BlogIndex']

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('image'),
        FieldPanel('intro'),
        FieldPanel('description'),
        FieldPanel('collection'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    api_fields = [
        APIField("get_child_pages", serializer=BlogPageChildSerializer()),
    ]

    def jpub(self):
        return jConvert(self.date)
    
    jpub.short_description = 'زمان انتشار'

    @property
    def get_child_pages(self):
        return self.get_children().public().live()

    def get_template(self, request, *args, **kwargs):
        return 'blog/blogsingle/blogsingle.html'

    def serve(self, request, *args, **kwargs):
        return render(
            request,
            self.get_template(request, *args, **kwargs),
        )

    class Meta:
        verbose_name = 'پست وبلاگ'
        verbose_name_plural = 'پست های وبلاگ'
