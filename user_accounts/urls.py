'''
Accounts urls configuration
'''

# Import all requirements
from django.urls import path
from allauth.account.views import LogoutView, PasswordSetView, PasswordChangeView, PasswordResetView
from .views import login_signup, CusLoginView, CusSignupView

urlpatterns = [
    path('', login_signup, name='login_or_signup'),
    path('login/', CusLoginView.as_view(), name='login'),
    path('signup/', CusSignupView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('set_password/', PasswordSetView.as_view(), name='set_password'),
    path('change_password/', PasswordChangeView.as_view(), name='change_password'),
    path('rest_password/', PasswordResetView.as_view(), name='rest_password'),
    #path('social/', ConnectionsView.as_view(), name='social'),
]
