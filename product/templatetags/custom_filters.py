from django import template

register = template.Library()

@register.filter
def calculate_subtotal(product):
    return product.price * product.quantity

@register.filter
def calculate_total_price(products):
    total_price = 0
    for product in products:
        total_price += product.price * product.quantity
    return total_price
