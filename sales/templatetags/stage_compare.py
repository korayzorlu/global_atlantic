from django import template

register = template.Library()


# https://stackoverflow.com/a/28513600/14506165
@register.simple_tag
def is_stage_lt(obj, value):
    return obj.is_lt(value)


@register.simple_tag
def is_stage_gt(obj, value):
    return obj.is_gt(value)


@register.simple_tag
def is_stage_finished(obj, value):
    return obj.is_stage_finished(value)
