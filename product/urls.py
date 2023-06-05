from product.views import cart_view, add_to_cart, remove_from_cart, update_cart, apply_discount, CheckoutView
from django.urls import path

urlpatterns = [
    path('cart/apply_discount/', apply_discount, name='apply_discount'),
    path('cart/remove/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('checkout/', CheckoutView, name='checkout'),
    path('', cart_view, name='cart'),
    ]