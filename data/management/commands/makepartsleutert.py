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
        data = pd.read_excel("./excelfile/parts-data-multiple.xlsx", "leutert price")
        df = pd.DataFrame(data)
        
        for i in range(len(df["MAKER"])):
            maker = Maker.objects.filter(name = df["MAKER"][i]).first()
            
            if not maker:
                maker = Maker.objects.create(
                        name = df["MAKER"][i]
                    )
                maker.save()
            
            if not pd.isnull(df["TYPE"][i]):
                makerType = MakerType.objects.filter(maker = maker, type = df["TYPE"][i]).first()
                
                if not makerType:
                    makerType = MakerType.objects.create(
                        maker = maker,
                        type = df["TYPE"][i]
                    )
                    makerType.save()
            else:
                makerType = None
                
            if pd.isnull(df["MANUFACTURER"][i]):
                manufacturer = ""
            else:
                manufacturer = df["MANUFACTURER"][i]
                
            if pd.isnull(df["RETAIL PRICE"][i]):
                retailPrice = 0
            else:
                retailPrice = df["RETAIL PRICE"][i]
                
            if pd.isnull(df["BUYING PRICE"][i]):
                buyingPrice = 0
            else:
                buyingPrice = df["BUYING PRICE"][i]
                
            startPartUniqueCodeValue = 1
            startPartUniqueValue = 101
                
            if pd.isnull(df["TECH SPEC"][i]):
                technicalSpecification = ""
                
                lastPartUnique = PartUnique.objects.filter().order_by('-code').first()
                if lastPartUnique:
                    newPartUnique = PartUnique(code = int(lastPartUnique.code) + 1)
                    newPartUnique.save()
                else:
                    newPartUnique = PartUnique(code = int(startPartUniqueValue))
                    newPartUnique.save()
                newPart = Part.objects.create(
                    maker = maker,
                    type = makerType,
                    partNo = df["PART NO"][i],
                    description = df["DESCRIPTION"][i],
                    techncialSpecification = technicalSpecification,
                    partUnique = newPartUnique,
                    partUniqueCode = startPartUniqueCodeValue,
                    retailPrice = retailPrice,
                    buyingPrice = buyingPrice,
                    manufacturer = manufacturer
                )
                newPart.save()
            else:
                technicalSpecification = df["TECH SPEC"][i]
                
                part = Part.objects.filter(techncialSpecification = df["TECH SPEC"][i]).order_by('-partUniqueCode').first()
                
                if part:
                    unique = part.partUnique
                    lastpartUniqueCode = part.partUniqueCode
                    newPart = Part.objects.create(
                        maker = maker,
                        type = makerType,
                        partNo = df["PART NO"][i],
                        description = df["DESCRIPTION"][i],
                        techncialSpecification = technicalSpecification,
                        partUnique = unique,
                        partUniqueCode = lastpartUniqueCode + 1,
                        retailPrice = retailPrice,
                        buyingPrice = buyingPrice,
                        manufacturer = manufacturer
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
                        type = makerType,
                        partNo = df["PART NO"][i],
                        description = df["DESCRIPTION"][i],
                        techncialSpecification = technicalSpecification,
                        partUnique = newPartUnique,
                        partUniqueCode = startPartUniqueCodeValue,
                        retailPrice = retailPrice,
                        buyingPrice = buyingPrice,
                        manufacturer = manufacturer
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