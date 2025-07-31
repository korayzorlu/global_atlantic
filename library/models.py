import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
# Create your models here.
from simple_history.models import HistoricalRecords

from ckeditor.fields import RichTextField
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model

from django_filters import FilterSet, ChoiceFilter