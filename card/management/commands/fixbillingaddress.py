from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from card.models import Vessel,Billing

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None

    def handle(self, *args, **options):
        user = User.objects.filter(username = "testuser").first()
        billings = Billing.objects.filter(sourceCompany = user.profile.sourceCompany)

        for billing in billings:
            address = billing.address
            address = address.replace("\n"," ")
            billing.address = address
            billing.save()