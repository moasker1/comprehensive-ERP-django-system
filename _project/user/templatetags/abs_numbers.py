from django import template

register = template.Library()

@register.filter
def abs_numbers(value):
    return abs(value)