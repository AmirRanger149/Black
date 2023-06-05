from .models import InventoryItem, ProductBrand, ProductVisit, CartItem
from index.extensions.group_list_convertor import group_list
from django.contrib.auth.decorators import login_required
from index.extensions.http_service import get_client_ip
from django.views.generic import ListView, DetailView
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.db.models import Count
from carton.cart import Cart


@login_required
def cart_view(request):
    cart = Cart(request.session)
    return render(request, 'products/cart/cart.html', {'cart': cart})


@login_required
def add_to_cart(request):
    cart = Cart(request.session)
    product_id = request.POST.get('InventoryItem_id')
    try:
        product = InventoryItem.objects.get(pk=product_id)
        if product.is_available:
            quantity_requested = int(request.POST.get('quantity', 1))
            if quantity_requested <= product.quantity:
                cart.add(product, price=product.price)
                message = f"محصول {product.product_title} با موفقیت به سبد خرید اضافه شد."
                response_data = {'success': True, 'message': message}
            else:
                message = "تعداد سفارش درخواستی بیشتر از موجودی محصول است."
                response_data = {'success': False, 'message': message}
        else:
            message = "موجودی محصول به پایان رسیده است."
            response_data = {'success': False, 'message': message}
    except InventoryItem.DoesNotExist:
        message = "محصول مورد نظر پیدا نشد."
        response_data = {'success': False, 'message': message}
    return JsonResponse(response_data)


@login_required
def remove_from_cart(request):
    cart = Cart(request.session)
    product_id = request.POST.get('InventoryItem_id')
    try:
        product = InventoryItem.objects.get(pk=product_id)
        cart.remove_single(product)
        message = f"محصول {product.product_title} با موفقیت از سبد خرید حذف شد."
        response_data = {'success': True, 'message': message}
    except InventoryItem.DoesNotExist:
        message = "محصول مورد نظر پیدا نشد."
        response_data = {'success': False, 'message': message}
    
    return JsonResponse(response_data)


'''
def update_cart_item(request, cart_item_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            cart_item.quantity = quantity
            cart_item.save()
            return redirect('cart')  # یا هر روتی که صفحه سبد خرید شما باشد
        except CartItem.DoesNotExist:
            return redirect('cart')  # یا هر روتی که صفحه سبد خرید شما باشد
    
    return render(request, 'update_cart_item.html')


class CartView(View):
    def get(self, request):
        cart = request.session.get("cart", [])
        products = InventoryItem.objects.live().filter(id__in=cart)
        return render(request, "utils/cart.html", {"products": products})

    def post(self, request):
        product_id = request.POST.get("product_id")
        if product_id:
            cart = request.session.get("cart", [])
            cart.append(int(product_id))
            request.session["cart"] = cart
        return redirect("cart")

class CheckoutView(View):
    def get(self, request):
        cart = request.session.get("cart", [])
        products = InventoryItem.objects.live().filter(id__in=cart)
        return render(request, "utils/checkout.html", {"products": products})

    def post(self, request):
        # پردازش فرآیند چک‌اوت و پرداخت
        # پاک کردن سبد خرید
        request.session["cart"] = []
        return redirect("checkout_success")
'''
'''
class ProductListView(ListView):
    template_name = 'product_module/product_list.html'
    model = Product
    context_object_name = 'products'
    ordering = ['-price']
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductListView, self).get_context_data()
        query = Product.objects.all()
        product: Product = query.order_by('-price').first()
        db_max_price = product.price if product is not None else 0
        context['db_max_price'] = db_max_price
        context['start_price'] = self.request.GET.get('start_price') or 0
        context['end_price'] = self.request.GET.get('end_price') or db_max_price
        context['banners'] = SiteBanner.objects.filter(is_active=True, position__iexact=SiteBanner.SiteBannerPositions.product_list)
        return context

    def get_queryset(self):
        query = super(ProductListView, self).get_queryset()
        category_name = self.kwargs.get('cat')
        brand_name = self.kwargs.get('brand')
        request: HttpRequest = self.request
        start_price = request.GET.get('start_price')
        end_price = request.GET.get('end_price')
        if start_price is not None:
            query = query.filter(price__gte=start_price)

        if end_price is not None:
            query = query.filter(price__lte=end_price)

        if brand_name is not None:
            query = query.filter(brand__url_title__iexact=brand_name)

        if category_name is not None:
            query = query.filter(category__url_title__iexact=category_name)
        return query


class ProductDetailView(DetailView):
    template_name = 'product_module/product_detail.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_product = self.object
        request = self.request
        favorite_product_id = request.session.get("product_favorites")
        context['is_favorite'] = favorite_product_id == str(loaded_product.id)
        context['banners'] = SiteBanner.objects.filter(is_active=True, position__iexact=SiteBanner.SiteBannerPositions.product_detail)
        galleries = list(Image.objects.filter(product_id=loaded_product.id).all())
        galleries.insert(0, loaded_product)
        context['product_galleries_group'] = group_list(galleries, 3)
        context['related_products'] = group_list(list(Product.objects.filter(brand_id=loaded_product.brand_id).exclude(pk=loaded_product.id).all()[:12]), 3)
        user_ip = get_client_ip(self.request)
        user_id = None
        if self.request.user.is_authenticated:
            user_id = self.request.user.id

        has_been_visited = ProductVisit.objects.filter(ip__iexact=user_ip, product_id=loaded_product.id).exists()

        if not has_been_visited:
            new_visit = ProductVisit(ip=user_ip, user_id=user_id, product_id=loaded_product.id)
            new_visit.save()

        return context


class AddProductFavorite(View):
    def post(self, request):
        product_id = request.POST["product_id"]
        product = Product.objects.get(pk=product_id)
        request.session["product_favorites"] = product_id
        return redirect(product.get_absolute_url())

'''


def product_brands_component(request: HttpRequest):
    product_brands = ProductBrand.objects.annotate(products_count=Count('product')).filter(is_active=True)
    context = {
        'brands': product_brands
    }
    return render(request, 'products/product_brands.html', context)