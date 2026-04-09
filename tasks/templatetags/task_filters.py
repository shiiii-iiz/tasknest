from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    return value.split(delimiter)

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []

@register.filter
def sub(value, arg):
    return value - arg

@register.filter
def pct(value, total):
    if total == 0:
        return 0
    return int((value / total) * 100)
