from django.core.management.base import BaseCommand, CommandError
from data.models import Part, PartUnique, Maker, MakerType
from sale.models import RequestPart

import os
import pandas as pd
from itertools import groupby
from operator import itemgetter

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        filePath = os.path.join(os.getcwd(), "excelfile")
        data = pd.read_excel(filePath + "/duplicated_parts_3.xlsx")
        df = pd.DataFrame(data)
        
        items = []
        
        for i in range(len(df["DUP"])):
            items.append({
                "id" : df["ID"][i],
                "maker" : df["Maker"][i],
                "type" : df["Type"][i],
                "partNo" : df["Part No"][i],
                "dup" : df["DUP"][i]
            })
            
        sorted_items = sorted(items, key=itemgetter('dup'))
        grouped_items = {dup: list(group) for dup, group in groupby(sorted_items, key=itemgetter('dup'))}
        
        for dup, group in grouped_items.items():
            for index, item in enumerate(group):
                if index == 0:
                    orgPart = Part.objects.filter(id = int(item["id"])).first()
                    print(f"org p id: {orgPart.id} - org p partNo: {orgPart.partNo}")
                part = Part.objects.filter(id = int(item["id"])).first()
                requestParts = RequestPart.objects.filter(part = part)
                print(f"old rp id: {part.id} - old rp partNo: {part.partNo}")
                for requestPart in requestParts:
                    requestPart.part = orgPart
                    requestPart.save()
                print(f"new rp id: {requestPart.part.id} - new rp partNo: {requestPart.part.partNo}")
                
        
        
        # grouped_dict = defaultdict(list)
        
        # for item in my_list:
        #     grouped_dict[item].append(item)

        # grouped_dict = dict(grouped_dict)