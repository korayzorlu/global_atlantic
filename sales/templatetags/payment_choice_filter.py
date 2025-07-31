from django import template
from sales.models import Quotation
register = template.Library()


@register.filter()
def get_choice_value(payment_model):
    for choice in Quotation.PAYMENT_CHOICES:
        if choice[0] == payment_model:
            return choice[1]
    return ''