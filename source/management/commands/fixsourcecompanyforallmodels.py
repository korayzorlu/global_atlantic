from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from django.apps import apps

from source.models import Company as SourceCompany

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        models = apps.get_models()
        esms = SourceCompany.objects.filter(companyNo = "SC-00000001").first()
        
        for model in models:
            modelName = model.__name__
            modelApp = model._meta.app_label
            modelFields = model._meta.get_fields()
            
            fieldNames = [modelField.name for modelField in modelFields]
            
            if "sourceCompany" in fieldNames:
                objects = model.objects.select_related().filter()
                objects.update(sourceCompany = esms)
                
            # if "sourceCompany" in fieldNames:
            #     print(f"{modelApp} || {modelName}")