from django import template

register = template.Library()

@register.filter(name='exist')
def exist(list):
    if list and len(list)>=1:
        return all(x is not None for x in list[0])
    else:
        return False