from django.core.management.base import BaseCommand, CommandError
from sale.models import OrderConfirmation,OrderTracking
from account.models import SendInvoice

import pandas as pd
import requests as rs
import xmltodict
import json

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        ocs = OrderConfirmation.objects.select_related("project").filter(project__stage = "order_tracking")

        for oc in ocs:
            sis = SendInvoice.objects.filter(orderConfirmation = oc)
            
            for si in sis:
                si.orderConfirmation.status = "invoiced"

                ot = OrderTracking.objects.get(project = oc.project)
                ot.invoiced = True
                ot.save()
                
                project = oc.project
                project.stage = "invoiced"
                project.save()
            
                oc.invoiced = True
                oc.sendInvoiced = True
                oc.save()
        