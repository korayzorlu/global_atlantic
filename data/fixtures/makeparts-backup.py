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
        data = pd.read_excel("./excelfile/parts-data.xlsx")
        df = pd.DataFrame(data)
        
        for i in range(len(df["Type"])):
            maker = Maker.objects.filter(name = df["Engine Builder"][i]).first()
            
            if maker:
                type = MakerType.objects.filter(maker = maker, type = df["Type"][i]).first()
                if not type:
                    type = MakerType.objects.create(
                        maker = maker,
                        type = df["Type"][i]
                    )
                    type.save()
            else:
                maker = Maker.objects.create(
                        name = df["Engine Builder"][i]
                    )
                type = MakerType.objects.create(
                        maker = maker,
                        type = df["Type"][i]
                    )
                maker.save()
                type.save()
                    
            part = Part.objects.filter(techncialSpecification = df["Techncial Specification"][i]).first()
            
            startPartUniqueCodeValue = 1
            startPartUniqueValue = 101
            
            if part:
                lastPart = Part.objects.filter(partUnique = part.partUnique).order_by('-partUniqueCode').first()
                if lastPart:
                    # En son oluşturulan nesnenin id'sini al
                    lastpartUniqueCode = lastPart.partUniqueCode
                else:
                    # Veritabanında hiç nesne yoksa, start_value değerini kullan
                    lastpartUniqueCode = startPartUniqueCodeValue - 1
                unique = part.partUnique
                partUniqueCode = int(lastpartUniqueCode) + 1
            else:
                lastPartUnique = PartUnique.objects.filter().order_by('-code').first()
                if lastPartUnique:  
                    newPartUnique = PartUnique(code = int(lastPartUnique.code) + 1)
                    newPartUnique.save()
                else:
                    newPartUnique = PartUnique(code = int(startPartUniqueValue))
                    newPartUnique.save()
                unique = newPartUnique
                partUniqueCode = int(startPartUniqueCodeValue)
            
            if pd.isnull(df["Group"][i]):
                group = ""
            else:
                group = df["Group"][i]
                
            if pd.isnull(df["Drawing Nr"][i]):
                drawingNr = ""
            else:
                drawingNr = df["Drawing Nr"][i]
                
            if pd.isnull(df["Drawing Nr"][i]):
                drawingNr = ""
            else:
                drawingNr = df["Drawing Nr"][i]
                
            if pd.isnull(df["Part No"][i]):
                partNo = ""
            else:
                partNo = df["Part No"][i]
                
            if pd.isnull(df["Description Of Goods"][i]):
                description = ""
            else:
                description = df["Description Of Goods"][i]
                
            if pd.isnull(df["Manufacturer"][i]):
                manufacturer = ""
            else:
                manufacturer = df["Manufacturer"][i]
            
            if pd.isnull(df["Techncial Specification"][i]):
                techncialSpecification = ""
            else:
                techncialSpecification = df["Techncial Specification"][i]
                
            if pd.isnull(df["Consumable"][i]):
                consumable = False
            else:
                consumable = True
                
            if pd.isnull(df["Cross Reference"][i]):
                crossRef = ""
            else:
                crossRef = df["Cross Reference"][i]
                
            if pd.isnull(df["ESMS Ref"][i]):
                ourRef = ""
            else:
                ourRef = df["ESMS Ref"][i]
            
            newPart = Part.objects.create(
                maker = maker,
                type = type,
                partUnique = unique,
                partUniqueCode = partUniqueCode,
                group = group,
                partNo = partNo,
                description = description,
                manufacturer = manufacturer,
                drawingNr = drawingNr,
                techncialSpecification = techncialSpecification,
                consumable = consumable,
                crossRef = crossRef,
                ourRef = ourRef
            )
            
            newPart.save()
            
            #self.stdout.write(group)