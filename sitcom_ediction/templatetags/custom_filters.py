from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """Replace all occurrences of a substring in the value with an empty string or another string."""
    return value.replace(arg, '')