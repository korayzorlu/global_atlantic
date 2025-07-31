import os

from django import template

register = template.Library()


# https://stackoverflow.com/a/4046508/14506165
# @register.filter
# def filenamee_beta(value):
#     return os.path.basename(str(value))
