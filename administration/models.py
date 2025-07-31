import datetime
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth import get_user_model

from django.utils import timezone

from user.utils import resize_image
from user.validators import ExtensionValidator

def cv_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.pk is None:
        return 'hr/user/temp/{0}/{1}'.format(instance.pk, "cv.pdf")
    else:
        return 'hr/user/{0}/documents/{1}'.format(instance.pk, "cv.pdf")

def nondisclosureAgreement_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.pk is None:
        return 'hr/user/temp/{0}/{1}'.format(instance.pk, "non-disclosure-agreement.pdf")
    else:
        return 'hr/user/{0}/documents/{1}'.format(instance.pk, "non-disclosure-agreement.pdf")

def contract_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.pk is None:
        return 'documents/user/temp/{0}/{1}'.format(instance.pk, filename)
    else:
        return 'documents/user/{0}/contract/{1}'.format(instance.pk, filename)

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="unknown")[0]

class AccessAuthorization(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="source_company_user")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    
    name = models.CharField(_("Name"), max_length=140, null=True, unique=True)
    code = models.CharField(_("Code"), max_length=140, null=True, unique=True)
    about = models.TextField(_("About"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"
    
class DataAuthorization(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="administration_data_authorization_user")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    
    name = models.CharField(_("Name"), max_length=140, null=True, unique=True)
    code = models.CharField(_("Code"), max_length=140, null=True, unique=True)
    about = models.TextField(_("About"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"
    
class ActionLog(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="action_log_user")
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]
    
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, blank=True, null=True)
    modelName = models.CharField(_("Model Name"), max_length=140, blank = True, null=True)
    objectId = models.IntegerField(_("Object Id"), blank = True, null = True)
    objectName = models.CharField(_("Object Name"), blank = True, null = True)
    actionLogDate = models.DateField(_("Action Log Date"), default = timezone.now, blank = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user} performed {self.get_action_display()} on {self.modelName} (ID: {self.objectId})"