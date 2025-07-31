from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from datetime import datetime

from .forms import *
from .models import *

def sendProcess(request,message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'private_' + str(request.user.id),
        {
            "type": "send_process",
            "message": message,
            "location" : location
        }
    )

class CalendarDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Calendar")
        elementTag = "calendar"
        elementTagSub = "calendarPart"
        
        context = {
                    "tag" : tag,
                    "elementTag": elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenilendiğinde doğrudan dashboard'a gider
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        
        return render(request, 'event/calendar.html', context)
    
class EventAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Event")
       
        if request.GET.get("title"):
            title = request.GET.get("title")
        else:
            title = ""
            
        if request.GET.get("text"):
            text = request.GET.get("text")
        else:
            text = ""
            
        if request.GET.get("startDate") == "Invalid Date":
            startDate = datetime.today().date()
        else:
            startDate = datetime.strptime(request.GET.get("startDate"), "%d/%m/%Y").date()
            
        if request.GET.get("endDate") == "Invalid Date":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("endDate"), "%d/%m/%Y").date()
        
        if request.GET.get("startTime") == "Invalid Date":
            startTime = datetime.today().time()
        else:
            startTime = datetime.strptime(request.GET.get("startTime"), "%H:%M:%S").time()
            
        if request.GET.get("endTime") == "Invalid Date":
            endTime = datetime.today().time()
        else:
            endTime = datetime.strptime(request.GET.get("endTime"), "%H:%M:%S").time()
        
        if request.GET.get("color"):
            color = request.GET.get("color")
        else:
            color = "cfe0fc"
        
        newEvent = Event.objects.create(
            title = title,
            description = text,
            startDate = startDate,
            endDate = endDate,
            startTime = startTime,
            endTime = endTime,
            color = color,
            user = request.user
        )
        
        newEvent.save()
        
        event = {}
        
        sendProcess(request,event,"event_add")
        
        return HttpResponse(status=204)

class EventUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Update Event")
        
        id = request.GET.get("id")
        
        if request.GET.get("title"):
            title = request.GET.get("title")
        else:
            title = ""
            
        if request.GET.get("text"):
            text = request.GET.get("text")
        else:
            text = ""
            
        if request.GET.get("startDate") == "Invalid Date":
            startDate = datetime.today().date()
        else:
            startDate = datetime.strptime(request.GET.get("startDate"), "%d/%m/%Y").date()
            
        if request.GET.get("endDate") == "Invalid Date":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("endDate"), "%d/%m/%Y").date()
        
        if request.GET.get("startTime") == "Invalid Date":
            startTime = datetime.strptime("00:00:00", "%H:%M:%S").time()
        else:
            startTime = datetime.strptime(request.GET.get("startTime"), "%H:%M:%S").time()
            
        if request.GET.get("endTime") == "Invalid Date":
            endTime = startTime = datetime.strptime("00:00:00", "%H:%M:%S").time()
        else:
            endTime = datetime.strptime(request.GET.get("endTime"), "%H:%M:%S").time()
        
        if request.GET.get("color"):
            color = request.GET.get("color")
        else:
            color = "cfe0fc"
            
        event = Event.objects.filter(id = id).first()
        
        event.title = title
        event.description = text
        event.startDate = startDate
        event.endDate = endDate
        event.startTime = startTime
        event.endTime = endTime
        event.color = color
        event.user = request.user
        
        event.save()
        
        return HttpResponse(status=204)
    
class EventDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Delete Event")
        
        id = request.GET.get("id")
            
        event = Event.objects.filter(id = id).first()
        
        event.delete()

        return HttpResponse(status=204)