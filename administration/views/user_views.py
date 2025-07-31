from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.hashers import make_password

from django.utils import timezone
from django.utils.formats import date_format
from datetime import date, timedelta, datetime
from urllib.parse import urlparse

import subprocess
from django.core import serializers
# Create your views here.

import telnetlib
from ..models import *
from ..forms import *

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

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
    
class UserDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Users")
        elementTag = "userList"
        elementTagSub = "userListPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'administration/user/users.html', context)

class UserAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add User")
        elementTag = "userList"
        elementTagSub = "userListPart"
        
        pageLoad(request,0,100,"false")
        
        form = UserForm(request.POST or None, request.FILES or None)
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
        
        return render(request, 'administration/user/user_add.html', context)
    def post(self, request, *args, **kwargs):
        pageLoad(request,0,100,"false")
        form = UserForm(request.POST, request.FILES or None)
        
        if form.is_valid():
            user = form.save(commit = False)
            
            if user.password != request.POST.get("passwordConfirm"):
                data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":"Passwords do not match"
                    }
                
                sendAlert(data,"default")
                return HttpResponse(status=404)
            elif user.first_name == "":
                data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":"First name cannot be empty"
                    }
                
                sendAlert(data,"default")
                return HttpResponse(status=404)
            elif user.last_name == "":
                data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":"Last name cannot be empty"
                    }
                
                sendAlert(data,"default")
                return HttpResponse(status=404)
            
            user.set_password(user.password)
            user.save()

            pageLoad(request,100,100,"true")

            return HttpResponse(status=204)
        else:
            print(form.errors)
            for item in form.errors:
                newDict = dict(form.errors.items())
                print(item)
                if item == "username":
                    data = {
                                "status":"secondary",
                                "icon":"triangle-exclamation",
                                "message":"Username already exists!"
                        }
                    
                    sendAlert(data,"default")


class UserUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("User Detail")
        elementTag = "userList"
        elementTagSub = "userListPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        pageLoad(request,20,100,"false")
        user = get_object_or_404(User, id = id)
        profile = get_object_or_404(Profile, user = id)
        pageLoad(request,40,100,"false")
        
        pageLoad(request,60,100,"false")
        pageLoad(request,80,100,"false")
        
        form = UserDetailForm(request.POST or None, request.FILES or None, instance = user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "profile" : profile,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "theUser" : user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'administration/user/user_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        user = get_object_or_404(User, id = id)
        profile = get_object_or_404(Profile, user = id)
        pageLoad(request,20,100,"false")
        
        form = UserDetailForm(request.POST, request.FILES or None, instance = user)
        if form.is_valid():
            user = form.save(commit = False)
            
            if request.POST.get("password"):
                if request.POST.get("password") != request.POST.get("passwordConfirm"):
                    data = {
                                "status":"secondary",
                                "icon":"triangle-exclamation",
                                "message":"Passwords do not match"
                        }
                    
                    sendAlert(data,"default")
                    return HttpResponse(status=404)
                else:
                    user.set_password(request.POST.get("password"))
            
            if user.first_name == "":
                data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":"First name cannot be empty"
                    }
                
                sendAlert(data,"default")
                return HttpResponse(status=404)
            elif user.last_name == "":
                data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":"Last name cannot be empty"
                    }
                
                sendAlert(data,"default")
                return HttpResponse(status=404)
            
            user.save()
            
            pageLoad(request,100,100,"true")
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)

class UserDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete User")
        elementTag = "userList"
        elementTagSub = "userListPart"
        
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
        
        return render(request, 'administration/user/user_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            user = get_object_or_404(User, id = int(id))
            profile = user.profile
            profile.delete()
            pageLoad(request,90,100,"false")
            user.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)

class UserSourceCompanyAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Source Company")
        elementTag = "userSourceCompany"
        elementTagSub = "userSourceCompanyPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        userId = refererPath.replace("/administration/user_update/","").replace("/","")
        theUser = get_object_or_404(User, id = id)
        form = UserSourceCompany(request.POST or None, request.FILES or None)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "theUser" : theUser,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'administration/user/user_source_company_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        # refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        # requestId = refererPath.replace("/sale/request_update/","").replace("/","")
        
        theUser = User.objects.get(id = id)
        
        sourceCompanies = request.POST.getlist("userSourceCompanies")
        
        for sourceCompany in sourceCompanies:
            theSourceCompany = SourceCompany.objects.filter(id = int(sourceCompany)).first()
            theUser.profile.sourceCompanyList.add(theSourceCompany)
            if len(theUser.profile.sourceCompanyList.all()) == 1:
                theUser.profile.sourceCompany = theSourceCompany
            theUser.profile.save()
        
        return HttpResponse(status=204)
        
class UserSourceCompanyDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Source Company")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'administration/user/user_source_company_delete.html', context)
    
    def post(self, request, list, id, *args, **kwargs):
        theUser = User.objects.get(id = id)
        
        idList = list.split(",")
        for id in idList:
            sourceCompany = get_object_or_404(SourceCompany, id = int(id))
            
            theUser.profile.sourceCompanyList.remove(sourceCompany)
            if theUser.profile.sourceCompany == sourceCompany:
                if len(theUser.profile.sourceCompanyList.all()) == 0:
                    theUser.profile.sourceCompany = None
                else:
                    theUser.profile.sourceCompany = theUser.profile.sourceCompanyList.all()[0]
            theUser.profile.save()
            
        return HttpResponse(status=204)
    