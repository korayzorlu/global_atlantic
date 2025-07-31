from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from data.models import ServiceCard
from source.models import Company as SourceCompany

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None
        
    def add_arguments(self, parser):
        parser.add_argument('app', type=str, help='App')
        parser.add_argument('model', type=str, help='Model')
        parser.add_argument('sc', type=str, help='Source Company')
        parser.add_argument('tc', type=str, help='Target Company')

    def handle(self, *args, **kwargs):
        app = kwargs['app']
        model = kwargs['model']
        sc = kwargs['sc']
        tc = kwargs['tc']
        
        try:
            Model = apps.get_model(app, model)
            
            objs = Model.objects.filter()
            print(objs)
            
            # sourceCompany = SourceCompany.objects.filter(companyNo = sc).first()
            # targetCompany = SourceCompany.objects.filter(companyNo = tc).first()
            
            # serviceCards = ServiceCard.objects.filter(sourceCompany = sourceCompany)
        except LookupError:
            print('Invalid App or Model!')
            return
        
        
        
        # for serviceCard in serviceCards:
        #     print(f"Old Id: {serviceCard.id} | Old Company: {serviceCard.sourceCompany.name}")
        #     serviceCard.pk = None
        #     serviceCard.sourceCompany = targetCompany
        #     serviceCard.save()
        #     print(f"New Id: {serviceCard.id} | New Company: {serviceCard.sourceCompany.name}")