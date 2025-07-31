from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Min, Q

from data.models import Part, PartUnique, Maker, MakerType
from sale.models import RequestPart

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        parts = Part.objects.filter(maker = 182)
        
        duplicateParts = Part.objects.values('partNo', 'description', 'techncialSpecification').annotate(count=Count('id')).filter(count__gt=1, maker = 182)

        for duplicatePart in duplicateParts:
            duplicatePartObjects = Part.objects.filter(partNo = duplicatePart["partNo"], description = duplicatePart["description"], techncialSpecification = duplicatePart["techncialSpecification"]).order_by("id")
            if duplicatePartObjects:
                parttss = []
                for duplicatePartObject in duplicatePartObjects:
                    parttss.append({"partNo" : duplicatePartObject.partNo,
                                    "description" : duplicatePartObject.description,
                                    "techncialSpecification" : duplicatePartObject.techncialSpecification,
                                    "id" : duplicatePartObject.id})
                parttss.pop(0)
                for partt in parttss:
                    deletePart = Part.objects.get(id = int(partt["id"]))
                    deletePart.delete()