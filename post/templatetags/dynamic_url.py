from django import template
from django.urls import reverse

register = template.Library()
@register.simple_tag
def dynamic_url(type,id=None):
    if id:
        return reverse(f'{type.lower()}_detail',args=[id])
    else:
        return reverse(f'{type.lower()}_list')