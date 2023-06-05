from index.extensions.jalali_converter import jalali_converter as jConvert
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

# Jalali calculator
@register.filter
def jpub(jtime):
    return jConvert(jtime.date)

jpub.short_description = 'زمان انتشار'