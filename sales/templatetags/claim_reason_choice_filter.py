from django import template
from sales.models import ClaimReason
register = template.Library()


@register.filter()
def get_choice_value(val):
    for choice in ClaimReason.CLAIM_REASON_CHOICES:
        if choice[0] is val:
            return choice[1]
    return ''