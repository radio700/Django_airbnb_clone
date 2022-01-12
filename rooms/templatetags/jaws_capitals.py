from django import template

register = template.Library()

@register.filter
def jaws_capitals(value):
    print(value)
    return value.capitalize()
