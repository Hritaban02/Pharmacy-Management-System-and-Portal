from django import template

register = template.Library()


@register.filter
def dictionary(value, arg):
    return value.get(arg)
