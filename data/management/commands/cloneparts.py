from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from data.models import ServiceCard, MakerType,Maker,PartUnique, Part
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
        parser.add_argument('makerr', type=str, help='Maker')
        parser.add_argument('sc', type=str, help='Source Company')
        parser.add_argument('tc', type=str, help='Target Company')

    def handle(self, *args, **kwargs):
        makerr = kwargs['makerr']
        sc = kwargs['sc']
        tc = kwargs['tc']
        
        sourceCompany = SourceCompany.objects.filter(companyNo = sc).first()
        targetCompany = SourceCompany.objects.filter(companyNo = tc).first()

        if int(makerr) != 0:
            theMaker = Maker.objects.filter(sourceCompany = sourceCompany, id = int(makerr)).first()
            objs = Part.objects.filter(sourceCompany = sourceCompany, maker = theMaker)
        elif int(makerr) == 0:
            objs = Part.objects.filter(sourceCompany = sourceCompany)

        objsPartUniques = [obj.partUnique.id for obj in objs]

        partUniques = PartUnique.objects.filter(sourceCompany = sourceCompany, id__in = objsPartUniques)
        
        for partUnique in partUniques:
            print(f"Old Id: {partUnique.id} | Old Company: {partUnique.sourceCompany.name}")
            
            partUniqueCheck = PartUnique.objects.filter(sourceCompany = targetCompany, code = partUnique.code).first()
            
            if not partUniqueCheck:
                partUnique.pk = None
                partUnique.sourceCompany = targetCompany
                partUnique.save()
                print(f"New Id: {partUnique.id} | New Company: {partUnique.sourceCompany.name}")
        
        for obj in objs:
            print(f"Old Id: {obj.id} | Old Companyy: {obj.sourceCompany.name}")
            
            if obj.maker:
                
                maker = Maker.objects.filter(sourceCompany = targetCompany, name = obj.maker.name).first()
                if not maker:
                    obj.maker.id = None
                    obj.maker.sourceCompany = targetCompany
                    obj.maker.save()

                    maker = obj.maker
            else:
                maker = None
                
            if obj.type:
                if obj.type.maker:
                    type = MakerType.objects.filter(sourceCompany = targetCompany, maker__name = obj.type.maker.name, type = obj.type.type).first()
                else:
                    type = MakerType.objects.filter(sourceCompany = targetCompany, type = obj.type.type).first()
            else:
                type = None
                
            oldPartUnique = obj.partUnique
            newPartUnique = PartUnique.objects.filter(code = oldPartUnique.code).first()
            
            objCheck = Part.objects.filter(sourceCompany = targetCompany, partUnique = newPartUnique, partUniqueCode = obj.partUniqueCode).first()
            if objCheck:
                print(f"Checked Id: {obj.id} | Checked Company: {obj.sourceCompany.name}")
            elif not objCheck:
                obj.pk = None
                obj.sourceCompany = targetCompany
                obj.maker = maker
                obj.type = type
                obj.partUnique = newPartUnique
                obj.save()
            
                print(f"New Id: {obj.id} | New Company: {obj.sourceCompany.name}")
        

# from data.models import Part,Maker,MakerType

# ps=Part.objects.select_related("maker","type").filter(sourceCompany=3)
    
# count=0       
# for p in ps:
#     count=count+1
#     esmsP = Part.objects.select_related("type").filter(sourceCompany=1,partUnique__code = p.partUnique.code,partUniqueCode=p.partUniqueCode).first()
    
#     if esmsP:
#         if esmsP.type:
#             type=MakerType.objects.select_related().filter(sourceCompany=3,maker=p.maker,type=esmsP.type.type).first()
#         else:
#             type=None
        
#         print(f"Old Maker: {p.maker} | Old Type: {p.type} | ESMS Part: {esmsP} | type: {type} | Index: {count}")
#         print(p)
#         p.type=type
#         p.save()
#         print(p)
#         print(f"New Maker: {p.maker} | New Type: {p.type} | ESMS Part: {esmsP} | type: {type} | Index: {count}")