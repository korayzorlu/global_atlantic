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
        
        for i in range(len(df["tech nr"])):
            maker = Maker.objects.filter(name = "MaK Caterpillar").first()
            
            if not maker:
                maker = Maker.objects.create(
                        name = "MaK"
                    )
                maker.save()

            # lastPartUnique = PartUnique.objects.filter().order_by('-code').first()
            # if lastPartUnique:  
            #     newPartUnique = PartUnique(code = int(lastPartUnique.code) + 1)
            #     newPartUnique.save()
            # else:
            #     newPartUnique = PartUnique(code = int(startPartUniqueValue))
            #     newPartUnique.save()
            # unique = newPartUnique
            # partUniqueCode = int(startPartUniqueCodeValue)
            
            if pd.isnull(df["tech nr"][i]):
                techSpec = ""
            else:
                techSpec = df["tech nr"][i]
                
            if pd.isnull(df["part nr"][i]):
                partNo = ""
            else:
                partNo = df["part nr"][i]
                
            if pd.isnull(df["description of goods"][i]):
                description = ""
            else:
                description = df["description of goods"][i]
                
            if pd.isnull(df["weight"][i]):
                weight = ""
            else:
                weight = df["weight"][i]
                
            part = Part.objects.filter(techncialSpecification = df["tech nr"][i]).order_by('-partUniqueCode').first()
            
            startPartUniqueCodeValue = 1
            startPartUniqueValue = 101
            
            if part:
                unique = part.partUnique
                lastpartUniqueCode = part.partUniqueCode
                newPart = Part.objects.create(
                    maker = maker,
                    partNo = partNo,
                    description = description,
                    weight = weight,
                    techncialSpecification = techSpec,
                    partUnique = unique,
                    partUniqueCode = lastpartUniqueCode + 1
                )
                newPart.save()
            else:
                lastPartUnique = PartUnique.objects.filter().order_by('-code').first()
                if lastPartUnique:
                    newPartUnique = PartUnique(code = int(lastPartUnique.code) + 1)
                    newPartUnique.save()
                else:
                    newPartUnique = PartUnique(code = int(startPartUniqueValue))
                    newPartUnique.save()
                newPart = Part.objects.create(
                    maker = maker,
                    partNo = partNo,
                    description = description,
                    weight = weight,
                    techncialSpecification = techSpec,
                    partUnique = newPartUnique,
                    partUniqueCode = startPartUniqueCodeValue
                )
                newPart.save()
            
                
            # startPartUniqueCodeValue = 1
            # startPartUniqueValue = 101
            
            # newPart = Part.objects.create(
            #     maker = maker,
            #     partNo = partNo,
            #     description = description,
            #     weight = weight,
            #     techncialSpecification = techSpec
            # )
            
            # if part:
            #     unique = part.partUnique
            #     lastPart = Part.objects.filter(partUnique = unique).order_by('-partUniqueCode').first()
            #     if lastPart:
            #         # En son oluşturulan nesnenin id'sini al
            #         lastpartUniqueCode = int(lastPart.partUniqueCode)
            #     else:
            #         # Veritabanında hiç nesne yoksa, start_value değerini kullan
            #         lastpartUniqueCode = int(startPartUniqueCodeValue) - 1
            #     newPart.partUnique = unique
            #     newPart.partUniqueCode = int(lastpartUniqueCode) + 1
            #     newPart.save()
            # else:
                
            #     lastPartUnique = PartUnique.objects.filter().order_by('-code').first()
                
            #     if lastPartUnique:  
            #         newPartUnique = PartUnique(code = int(lastPartUnique.code) + 1)
            #         newPart.save()
            #     else:
            #         newPartUnique = PartUnique(code = int(startPartUniqueValue))
            #         newPart.save()
                
            #     newPart.partUnique = newPartUnique
            #     newPart.partUniqueCode = int(startPartUniqueCodeValue)
            #     newPart.save()
            # newPart.save()
            
            #self.stdout.write(group)