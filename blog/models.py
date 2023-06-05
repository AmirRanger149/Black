"""
2020 Black
developer : #ABS
"""

# Import all requirements
from index.extensions.jalali_converter import jalali_converter as jConvert
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.contrib.routable_page.models import RoutablePageMixin
from modelcluster.contrib.taggit import ClusterTaggableManager
from user_accounts.models import user_accounts as User
from wagtail.snippets.models import register_snippet
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

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        all_posts = BlogPage.objects.live().public().order_by('-first_published_at')

        if request.GET.get('tag', None):
            tags = request.GET.get('tag')
            all_posts = all_posts.filter(tags__slug__in=[tags])

        # Paginate all posts by 6 per page
        paginator = Paginator(all_posts, 6)
        # Try to get the ?page=x value
        page = request.GET.get("page")
        try:
            # If the page exists and the ?page=x is an int
            posts = paginator.page(page)
        except PageNotAnInteger:
            # If the ?page=x is not an int; show the first page
            posts = paginator.page(1)
        except EmptyPage:
            # If the ?page=x is out of range (too high most likely)
            # Then return the last page
            posts = paginator.page(paginator.num_pages)

        # "posts" will have child pages; you'll need to use .specific in the template
        # in order to access child properties, such as youtube_video_id and subtitle
        context["posts"] = posts
        return context

    def serve(self, request, *args, **kwargs):
        return render(
            request,
            self.get_template(request, *args, **kwargs),
            self.context(request, *args, **kwargs),
        )

    class Meta:
        verbose_name = 'صفحه اصلی وبلاگ'


# blog page model
class BlogPage(Page):
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

    class Meta:
        verbose_name = 'پست وبلاگ'
        verbose_name_plural = 'پست های وبلاگ'

    # Jalali calculator

    def jpub(self):
        return jConvert(self.date)

    def get_template(self, request, *args, **kwargs):

        return 'blog/blogsingle/blogsingle.html'

    def serve(self, request, *args, **kwargs):
        return render(
            request,
            self.get_template(request, *args, **kwargs),
        )
    
    jpub.short_description = 'زمان انتشار'
