import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
# Create your models here.
from simple_history.models import HistoricalRecords

from ckeditor.fields import RichTextField

from user.models import Team, Profile

class Note(models.Model):
    """
    Stores the note
    """
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="note_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.DO_NOTHING, null=True,blank = True)
    title = models.CharField(_("Title"), max_length=50, blank = True, null = True)
    text = models.TextField(_("Text"), max_length=500, blank = True, null = True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ['-created_date']