from django import template
register = template.Library()

@register.filter(name='keywords')
def keywords(value):
    return value.split(' ')
