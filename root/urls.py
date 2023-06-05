"""
2020 Black
root URL configuration
developer : #ABS
"""

# Import all requirements
from product.views import cart_view, add_to_cart, remove_from_cart, update_cart, apply_discount, CheckoutView
from .local_settings import DEVELOPERS_PANEL, ADMINS_PANEL
from wagtail.documents import urls as wagtaildocs_urls
from django.conf.urls import handler404, handler500
from wagtail.admin import urls as wagtailadmin_urls
from django.views.generic.base import RedirectView
from django.urls import include, path, re_path
from django.conf.urls.static import static
from wagtail import urls as wagtail_urls
from django.contrib import admin
from django.conf import settings
from .api import api_router
import os.path


# NOTE : PLEASE KEEP THIS FILE SAFE !
urlpatterns = [
    path('cart/apply_discount/', apply_discount, name='apply_discount'),
    path('cart/remove/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('api-auth/', include('rest_framework.urls')),
    path('checkout/', CheckoutView, name='checkout'),
    path('accounts/', include('user_accounts.urls')),
    path('UsersAccounts/', include('allauth.urls')),
    path(ADMINS_PANEL, include(wagtailadmin_urls)),
    path('UNIQUEDOC/', include(wagtaildocs_urls)),
    path(DEVELOPERS_PANEL, admin.site.urls),
    path('cart/', cart_view, name='cart'),
    path('api/', api_router.urls),

    re_path(r'', include(wagtail_urls)),
]

# Custom static & storage files configuration
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL + 'images/', document_root=os.path.join(settings.MEDIA_ROOT, 'images'))
urlpatterns += [
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'blog/images/favicon.ico'))
]

# Add the 404-500 error view
handler404 = 'index.views.page_not_found_error'
handler500 = 'index.views.server_error'