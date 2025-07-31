from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.utils import timezone

from data.models import Part, PartUnique, Maker, MakerType
from sale.models import RequestPart
from user.models import Record

import os
import pandas as pd
from itertools import groupby
from operator import itemgetter
from datetime import datetime

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None
    
    def handle(self, *args, **settings):

        Record.objects.all().delete()

        
