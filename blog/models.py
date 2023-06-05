"""
2020 Black
developer : #ABS
"""

# Import all requirements
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from user_accounts.models import user_accounts as User
from wagtail.snippets.models import register_snippet
from django.http import HttpRequest, JsonResponse
from wagtail.api.v2.views import PagesAPIViewSet
from django.shortcuts import render, redirect
from wagtail.models import Page, PageManager
from wagtail.admin.panels import FieldPanel
from taggit.models import TaggedItemBase
from wagtail.fields import RichTextField
from django.utils import timezone
from wagtail.search import index
from django.db import models


# Blog Page Manager
class BlogPageManager(PageManager):
    ''' 
    DEVELOPMENT BY #ABS 
    '''
    pass


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

    @property
    def get_child_pages(self):
        return self.get_children().public().live()

    def get_template(self, request, *args, **kwargs):

        return 'blog/blogarchive/blogarchive.html'

    def serve(self, request, *args, **kwargs):
        # serve data and send http Response
        self.get_template(request, *args, **kwargs),
        return render(request, template, context)

    class Meta:
        verbose_name = 'صفحه اصلی وبلاگ'


# blog page model
class BlogPage(Page, RoutablePageMixin):
    comments = models.ManyToManyField('index.Comments', blank=True)
    owner: models.ForeignKey(User, blank=True, on_delete=models.SET_NULL,)
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
    description = models.CharField(max_length=25, verbose_name='توضیحات کامل پست')

    subpage_types = []
    parent_page_types = ['BlogIndex']
    
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('image'),
        FieldPanel('intro'),
        FieldPanel('description'),
        FieldPanel('collection'),
    ]

    def to_json(self):
        return {
            'title': self.title,
            'owner': self.owner.username if self.owner else '',
            'comments': self.comments.count(),
            'image': self.image.url if self.image else '',
            'collection': self.collection.title if self.collection else '',
            'intro': self.intro,
            'date': self.date.strftime('%Y-%m-%d'),
            'body': self.body,
            'description': self.description,
        }

    def get_template(self, request, *args, **kwargs):
        return 'blog/blogsingle/blogsingle.html'

    @route(r'^json/$', name='blog_page_json')
    def serve(self, request, *args, **kwargs):
        # serve data and send http Response and json Response
        if request.GET.get('json', False):
            json_data = {'posts': self.to_json()}
            return JsonResponse(json_data)
        return super().serve(request, *args, **kwargs)

    class Meta:
        verbose_name = 'پست وبلاگ'
        verbose_name_plural = 'پست های وبلاگ'
