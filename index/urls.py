from django.urls import path
from blog.views import blog_post_list

urlpatterns = [
    path('blog/posts', blog_post_list, name='rest_blog_posts'),
]