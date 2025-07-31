from django import template
from sales.models import InquiryPart
register = template.Library()


@register.filter()
def get_availability_choice_value(availability_model):
    for choice in InquiryPart.AVAILABILITY_CHOICES:
        if choice[0] == availability_model:
            return choice[1]
    return ''