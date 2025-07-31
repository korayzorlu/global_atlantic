from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage, send_mail
# Create your views here.
from django.views import View
from django.views.decorators.cache import cache_page
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Template
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import close_old_connections

from ..forms import *
from ..tasks import *
from ..pdfs.project_pdfs import *

import pandas as pd
import json
import random
import string
from datetime import datetime
import time

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpProject'

def sendAlert(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "send_alert",
            "message": message,
            "location" : location
        }
    )

def pageLoad(request,percent,total,ready):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'private_' + str(request.user.id),
        {
            "type": "send_percent",
            "message": percent,
            "location" : "page_load",
            "totalCount" : total,
            "ready" : ready
        }
    )

def reloadTable(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "reload_table",
            "message": message,
            "location" : location
        }
    )
    
class ProjectDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Projects")
        elementTag = "project"
        elementTagSub = "projectPart"
        
        pageLoad(request,0,100,"false")
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")

        return render(request, 'purchasing/project/projects.html', context)
    
class ProjectAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Project")
        elementTag = "project"
        elementTagSub = "projectPart"
        elementTagId = "new"
        
        pageLoad(request,0,100,"false")
        
        form = ProjectForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'purchasing/project/project_add.html', context)
    
    def post(self, request, *args, **kwargs):
        elementTag = "project"
        elementTagSub = "projectPart"
        elementTagId = "new"

        pageLoad(request,0,100,"false")
        form = ProjectForm(request.POST, request.FILES or None, user = request.user)
        
        if form.is_valid():
            project = form.save(commit = False)
            project.sourceCompany = request.user.profile.sourceCompany
            project.user = request.user
            
            identificationCode = request.user.profile.sourceCompany.purchasingProjectCode
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastProject = Project.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            pageLoad(request,20,100,"false")
            
            if lastProject:
                lastCode = lastProject.code
            else:
                lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            project.code = code
            
            project.yearCode = yearCode
            
            projectNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
            project.projectNo = projectNo
            
            project.save()
            pageLoad(request,60,100,"false")
            project.sessionKey = request.session.session_key
            project.stage = "project"
            project.save()

            pageLoad(request,100,100,"true")

            return HttpResponse(status=204)
        else:
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"triangle-exclamation",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
    
class ProjectUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Project Detail")
        elementTag = "project"
        elementTagSub = "projectPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        projects = Project.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        pageLoad(request,20,100,"false")
        project = get_object_or_404(Project, id = id)
        pageLoad(request,80,100,"false")
        
        form = ProjectForm(request.POST or None, request.FILES or None, instance = project, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "projects" : projects,
                "project" : project,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'purchasing/project/project_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "project"
        elementTagSub = "projectPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        project = get_object_or_404(Project, id = id)
        identificationCode = project.identificationCode
        code = project.code
        yearCode = project.yearCode
        projectNo = project.projectNo
        sessionKey = project.sessionKey
        sourceCompany = project.sourceCompany
        user = project.user
        pageLoad(request,20,100,"false")
        form = ProjectForm(request.POST, request.FILES or None, instance = project, user = request.user)
        if form.is_valid():
            project = form.save(commit = False)
            project.sourceCompany = sourceCompany
            project.identificationCode = identificationCode
            project.code = code
            project.yearCode = yearCode
            project.projectNo = projectNo
            project.sessionKey = sessionKey
            project.user = user
            project.save()
            
            pageLoad(request,100,100,"true")
            
            data = {
                        "block":f"message-container-{elementTag}-{elementTagId}",
                        "icon":"circle-check",
                        "message":"Saved"
                }
            
            sendAlert(data,"form")
            return HttpResponse(status=204)
            
        else:
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"triangle-exclamation",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)

class ProjectDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Project")
        elementTag = "project"
        elementTagSub = "projectPart"
        
        idList = list.split(",")
        elementTagId = idList[0]
        for id in idList:
            print(int(id))
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'purchasing/project/project_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            project = get_object_or_404(Project, id = int(id))
            pageLoad(request,90,100,"false")
            #process status sil
            processStatus = project.process_status_purchasing_project.first()
            if processStatus:
                processStatus.delete()
            #process status sil-end
            project.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
    

class ProjectItemAddTypeView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Project Item Type")
        elementTag = "projectItem"
        elementTagSub = "projectItemPart"
        
        project = get_object_or_404(Project, id = id)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "project" : project
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'purchasing/project/project_item_add_type.html', context)
    
class ProjectItemAddView(LoginRequiredMixin, View):

    def get(self, request, id, *args, **kwargs):
        tag = _("Add Project Item")
        elementTag = "projectItem"
        elementTagSub = "projectItemPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        project = get_object_or_404(Project, id = id)
        
        if is_ajax(request=request):
            term = request.GET.get("term")
            parts = Part.objects.filter(sourceCompany = request.user.profile.sourceCompany,maker = project.maker, partNo__icontains = term)
            if len(parts) == 0:
                parts = Part.objects.filter(sourceCompany = request.user.profile.sourceCompany,maker = project.maker, group__icontains = term)
            response_content = list(parts.values())
            
            return JsonResponse(response_content, safe=False)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "project" : project
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'purchasing/project/project_item_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        data = {"tableName":"projectPart-" + str(id)}       
        reloadTable(data,"start")
        
        project = Project.objects.get(id = id)
        projectItems = ProjectItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,project = project)
        sequencyCount = len(projectItems)
        items = []
        
        for projectItem in projectItems:
            if projectItem.part:
                items.append(projectItem.part)
            elif projectItem.serviceCard:
                items.append(projectItem.serviceCard)
            if projectItem.expense:
                items.append(projectItem.expense)
        
        projectItems = request.POST.getlist("projectItems")
        
        for item in projectItems:
            if request.GET.get("type") == "part":
                part = Part.objects.get(id = int(item))
                if part.maker:
                    if part.type:
                        name = part.maker.name + " " + part.type.type + " " + part.partNo
                    else:
                        name = part.maker.name + " " + part.partNo
                else:
                    name = part.partNo
                description = part.description
                unit = part.unit
            else:
                part = None
            newProjectItem = ProjectItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    project = project,
                    part = part,
                    name = name,
                    description = description,
                    unit = unit,
                    quantity = 1,
                    sequency = sequencyCount + 1
                )
            newProjectItem.save()
            
            sequencyCount = sequencyCount + 1
        
        data = {"tableName":"projectPart-" + str(id)}       
        reloadTable(data,"stop")
        
        return HttpResponse(status=204)
    
class ProjectItemDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Project Item")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'purchasing/project/project_item_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        projectItem = get_object_or_404(ProjectItem, id = int(idList[0]))
        
        data = {"tableName":"projectPart-" + str(projectItem.project.id)}       
        reloadTable(data,"start")
        
        idList = list.split(",")
        for id in idList:
            projectItem = get_object_or_404(ProjectItem, id = int(id))
            projectItem.delete()
        
        data = {"tableName":"projectPart-" + str(projectItem.project.id)}       
        reloadTable(data,"stop")
        
        return HttpResponse(status=204)
    