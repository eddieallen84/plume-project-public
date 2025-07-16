from django import template
import pprint

register = template.Library()

@register.filter(name='get_range')
def get_range(value):
    return range(value)

@register.filter(name='pprint')
def pretty_print(value):
    return pprint.pformat(value)