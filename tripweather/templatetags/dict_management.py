from django import template
from django.template import Template

register = template.Library()

@register.filter
def hash(h, key):
    return h[key]