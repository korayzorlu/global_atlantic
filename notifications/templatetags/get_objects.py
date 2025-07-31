import os

from django import template

register = template.Library()


# https://stackoverflow.com/a/4046508/14506165
@register.filter
def get_relationed_object(obj):
    return obj.get_relationed_object()

@register.filter
def get_optional_object(obj):
    return obj.get_optional_object()

@register.filter
def get_relationed_object_no(obj):
    return obj.get_optional_object().no

@register.filter
def get_optional_object_no(obj):
    return obj.get_optional_object().no
