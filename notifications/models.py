from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import datetime

from sales.models import Project, Quotation
# Create your models here.

class Notification(models.Model):
    """Notification Model"""
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="notification_source_company")
    MESSAGE = 'message'
    CONFIRMATION = 'confirmation'
    NOTIFICATION_TYPE_CHOICES = (
        (MESSAGE, _('Message')),
        (CONFIRMATION, _('Confirmation'))
    )
    
    to_user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    url_key = models.CharField(max_length=80, default="")
    relationed_object_id = models.IntegerField(null=True, blank=True)
    optional_id = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        if self.notification_type == self.MESSAGE:     
            return  f"{self.to_user} has {self.notification_type}"
        elif self.notification_type == self.CONFIRMATION:
             return  f"{self.relationed_object_id}. project's {self.optional_id} id quotation has {self.notification_type}"
    
    def get_relationed_object(self):
        if self.notification_type == self.CONFIRMATION:
            if Project.objects.get(id = self.relationed_object_id):
                return Project.objects.get(id = self.relationed_object_id)

    def get_optional_object(self):
        if self.notification_type == self.CONFIRMATION:
            if Quotation.objects.get(id = self.optional_id):
                return Quotation.objects.get(id = self.optional_id)
    
    @staticmethod
    def get_last_notification_update_time():
        ordered_notifications = Notification.objects.all().order_by('-updated_at').first()
        if ordered_notifications:
            return ordered_notifications.updated_at
        else:
            return datetime.datetime(1, 1, 1, tzinfo=datetime.timezone.utc)
    class Meta:
        ordering = ['-created_at']
        
class Notify(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="notify_source_company")
    message = models.CharField(max_length=100)
    
    def __str__(self):
        return self.message