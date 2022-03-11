from django import template

register = template.Library()


@register.filter
def mult(value, arg):
    return value * arg
