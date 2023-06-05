from index.extensions.jalali_converter import jalali_converter as jConvert
from django import template


register = template.Library()

@register.filter
    # Jalali calculator
    def jpub(jtime):
        return jConvert(jtime.date)