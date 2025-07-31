from django.core.management.base import BaseCommand, CommandError
from data.models import Part, PartUnique, Maker, MakerType

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        makers = Maker.objects.filter()
        
        for maker in makers:
            maker.delete()