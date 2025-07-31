from django import template

from user.models import Currency

register = template.Library()


# https://stackoverflow.com/a/28513600/14506165
@register.filter()
def get_currency_unit_price(obj):
    return obj.get_currency_unit_price()

@register.filter()
def get_currency_total_price_1(obj):
    return obj.get_currency_total_price_1()

@register.filter()
def get_total_price_2(obj):
    return obj.get_total_price_2()
        
   