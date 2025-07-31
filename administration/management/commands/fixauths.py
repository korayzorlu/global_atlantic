from django.core.management.base import BaseCommand, CommandError
from sale.models import QuotationPart,Quotation
from account.models import ProformaInvoicePart, SendInvoicePart, ProformaInvoice, SendInvoice,Payment, IncomingInvoice,ServiceSendInvoice, Process

from ...models import AccessAuthorization,DataAuthorization
from user.models import AccessAuthorization as AccessAuth
from user.models import DataAuthorization as DataAuth
from user.models import Profile

import pandas as pd
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        profiles = Profile.objects.filter()
        
        for profile in profiles:
            newAccessAuthorization = AccessAuthorization.objects.filter(code = profile.accessAuthorization.code).first()
