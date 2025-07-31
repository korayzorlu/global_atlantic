from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from notifications.models import Notification
# Create your views here.

from django.utils.translation import gettext_lazy as _
from django.contrib import messages

class NotificationsDataView(LoginRequiredMixin, View):
    def get(self, request, notification_id, *args, **kwargs):        
        notification = get_object_or_404(Notification, pk=notification_id)
        notification.is_read = True
        notification.save()
        
        if notification.notification_type == Notification.CONFIRMATION:
            return redirect(notification.url_key, notification.relationed_object_id ,notification.optional_id)
        
class MessageUpdateSuccessDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Message")
        
        messages.success(request, "Successfully!")
    
        context = {
                    "tag" : tag
            }
        return HttpResponse(status=204)
    
class MessageUpdateErrorDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Message")
        
        messages.error(request, "Successfully!")
    
        context = {
                    "tag" : tag
            }
        return HttpResponse(status=204)