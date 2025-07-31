import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
# Create your models here.
from simple_history.models import HistoricalRecords

from ckeditor.fields import RichTextField
from django.utils import timezone

from user.models import Team, Profile

class Event(models.Model):
    """
    Stores the note
    """
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="event_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.DO_NOTHING, blank = True)
    title = models.CharField(_("Title"), max_length=200, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    allDay = models.BooleanField(_("All Day"), default = True)
    startDate = models.DateField(_("Start Date"), default = timezone.now, blank = True)
    endDate = models.DateField(_("End Date"), default = timezone.now, blank = True)
    startTime = models.TimeField(_("Start Time"), default = timezone.now, blank = True)
    endTime = models.TimeField(_("End Time"), default = timezone.now, blank = True)
    
    COLORS = (
        ('cfe0fc', _('#cfe0fc')),
        ('ebcdfe', _('#ebcdfe')),
        ('c7f5d9', _('#c7f5d9')),
        ('fdd8de', _('#fdd8de')),
        ('ffebc2', _('#ffebc2')),
        ('d0f0fb', _('#d0f0fb')),
        ('292929', _('#292929')),
    )
    
    color = models.CharField(_("Color"), max_length=40, default="cfe0fc", blank= True, null=True, choices = COLORS)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ['-created_date']