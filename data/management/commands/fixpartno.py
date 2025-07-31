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
        data = pd.read_excel("./excelfile/fix-part-no.xlsx", "Quotation")
        df = pd.DataFrame(data)
        
        for i in range(len(df["Line"])):
            part = Part.objects.select_related().filter(id = int(df["ID"][i])).first()
            
            if pd.isnull(df["Part No"][i]):
                partNo = ""
            else:
                partNo = df["Part No"][i]
                
            if pd.isnull(df["Part No Old"][i]):
                partNoOld = ""
            else:
                partNoOld = df["Part No Old"][i].replace(" - ","-")
            
            part.partNo = partNoOld
            part.save()
            
            print("part no: " + partNoOld + " || old part no: " + partNoOld)