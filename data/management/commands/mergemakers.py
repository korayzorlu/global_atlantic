from django.core.management.base import BaseCommand, CommandError
from django.apps import apps

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

    def add_arguments(self, parser):
        parser.add_argument('source_maker', type=str, help='Source Maker')
        parser.add_argument('target_maker', type=str, help='Target Maker')
    
    def handle(self, *args, **kwargs):
        sourceMakerId = kwargs['source_maker']
        targetMakerId = kwargs['target_maker']

        def get_related_models(model_class):
            related_models = []
            # Modelin kendisine ForeignKey ile bağlı olan modelleri bul
            for related_object in model_class._meta.related_objects:
                related_models.append(related_object.related_model)
            return related_models
        
        related_models = get_related_models(Maker)

        sourceMaker = Maker.objects.filter(id = sourceMakerId).first()
        targetMaker = Maker.objects.filter(id = targetMakerId).first()

        sourceMakerTypes = MakerType.objects.filter(maker = sourceMaker)
        targetMakerTypes = MakerType.objects.filter(maker = targetMaker)

        targetMakerTypesList = [targetMakerType.type for targetMakerType in targetMakerTypes]

        for sourceMakerType in sourceMakerTypes:
            if sourceMakerType.type in targetMakerTypesList:
                print(f"var: {sourceMakerType}")

        if sourceMaker and targetMaker:
            print(f"source maker: {sourceMaker} | target maker: {targetMaker}\n    processing...")

            for model in related_models:
                relatedObjects = model.objects.filter(maker = sourceMaker)
                for relatedObject in relatedObjects:
                    print(f"model: {model.__name__} | object: {relatedObject}")
                    #relatedObject.maker = targetMaker
                    #relatedObject.save()

                    if not model.__name__ == "MakerType":
                        try:
                            if relatedObject.makerType:
                                if relatedObject.makerType.type in targetMakerTypesList:
                                    type = MakerType.objects.filter(maker = relatedObject.targetMaker, type = relatedObject.makerType.type).first()
                                    print(f"old type: {relatedObject.makerType} | new type: {type}")
                        except Exception as e:
                            print(e)
        else:
            print(f"no maker data xdf")
