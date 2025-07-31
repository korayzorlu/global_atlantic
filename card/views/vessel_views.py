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
import asyncio

from ..forms import *
from ..tasks import *
from account.models import SendInvoice

import pandas as pd
from validate_email import validate_email
import json
from operator import itemgetter

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
  

def matchMikro(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "match_mikro",
            "message": message,
            "location" : location
        }
    )
    
class VesselDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Vessels")
        elementTag = "vessel"
        elementTagSub = "vesselPerson"
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        
        context = {
                    "tag" : tag,
                    "elementTagSub" : elementTagSub,
                    "elementTag" : elementTag
            }
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'card/vessels.html', context)
    
class VesselAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Vessel")
        elementTag = "vessel"
        elementTagSub = "vesselPerson"
        elementTagId = "new"
        form = VesselForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "form" : form
        }
        return render(request, 'card/vessel_add.html', context)
    
    def post(self, request, *args, **kwargs):
        elementTag = "vessel"
        elementTagSub = "vesselPerson"
        elementTagId = "new"
        form = VesselForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            vessel = form.save()
            vessel.sourceCompany = request.user.profile.sourceCompany
            vessel.save()
            
            sessionPersons = Person.objects.filter(sourceCompany = request.user.profile.sourceCompany,sessionKey = request.session.session_key, user = request.user, vessel = None)
            for sessionPerson in sessionPersons:
                sessionPerson.vessel = vessel
                sessionPerson.save()
                
            return HttpResponse(status=204)
        else:
            print(form.errors)
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"circle-check",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
        
class VesselUpdateModalView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Update Vessel")
        elementTag = "vessel"
        elementTagSub = "vesselPerson"
        elementTagId = id

        vessels = Company.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        vessel = get_object_or_404(Vessel, id = id)
        form = VesselForm(request.POST or None, request.FILES or None, instance = vessel, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "form" : form,
                "vessels" : vessels,
                 "vessel" : vessel
         }
        return render(request, 'card/vessel_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "vessel"
        elementTagSub = "vesselPerson"
        elementTagId = id

        vessel = get_object_or_404(Vessel, id = id)
        sourceCompany = vessel.sourceCompany
        form = VesselForm(request.POST, request.FILES or None, instance = vessel, user=request.user)
        if form.is_valid():
            vessel = form.save(commit = False)
            vessel.sourceCompany = sourceCompany
            vessel.save()
            return HttpResponse(status=204)
        else:
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"circle-check",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
        
class VesselUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Vessel Detail")
        elementTag = "vessel"
        elementTagSub = "vesselPerson"
        elementTagId = id
        
        vessels = Vessel.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        vessel = get_object_or_404(Vessel, id = id)
        
        historyRecords = []
        for history in vessel.history.all().order_by("history_date"):
            historyRecords.append({
                "value" : history.imo,
                "date" : history.history_date
            })
            
        uniqueHistory = []
        previousValue = None
        for history in historyRecords:
            if history["value"] != previousValue:
                uniqueHistory.append({
                    "value" : history["value"],
                    "date" : history["date"]
                })
                previousValue = history["value"]
        
        print(list(reversed(uniqueHistory)))
        
        form = VesselForm(request.POST or None, request.FILES or None, instance = vessel, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "vessels" : vessels,
                "vessel" : vessel
        }
        return render(request, 'card/vessel_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "vessel"
        elementTagSub = "vesselPerson"
        elementTagId = id

        vessel = get_object_or_404(Vessel, id = id)
        sourceCompany = vessel.sourceCompany
        form = VesselForm(request.POST, request.FILES or None, instance = vessel, user = request.user)
        if form.is_valid():
            vessel = form.save(commit = False)
            vessel.sourceCompany = sourceCompany
            vessel.save()
            
            sessionPersons = Person.objects.filter(sourceCompany = request.user.profile.sourceCompany,sessionKey = request.session.session_key, user = request.user, vessel = None)
            for sessionPerson in sessionPersons:
                sessionPerson.vessel = vessel
                sessionPerson.save()
                
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
                "icon":"circle-check",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
        
class VesselDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Vessel")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        return render(request, 'card/vessel_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            vessel = get_object_or_404(Vessel, id = int(id))
            vessel.delete()
        return HttpResponse(status=204)

class EnginePartInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Engine Part")
        elementTag = "vessel"
        elementTagSub = "vesselPerson"
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        vesselId = refererPath.replace("/card/vessel_update/","").replace("/","")
        vessel = get_object_or_404(Vessel, id = id)
        
        form = EnginePartForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "vessel" : vessel,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'card/engine_part_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        vesselId = refererPath.replace("/card/vessel_update/","").replace("/","")
        
        vessel = Vessel.objects.get(id = id)
        
        form = EnginePartForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            enginePart = form.save(commit = False)
            enginePart.sourceCompany = request.user.profile.sourceCompany
            
            enginePart.user = request.user
            enginePart.vessel = vessel
            enginePart.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form,
                    "vesselId" : vesselId
            }
            return render(request, 'card/engine_part_add_in_detail.html', context)

class EnginePartDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Engine Part")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'card/engine_part_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            enginePart = get_object_or_404(EnginePart, id = int(id))
            enginePart.delete()
        return HttpResponse(status=204)
   
class PersonAddInCompanyView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Person")
        elementTagSub = "companyPerson"
        form = PersonForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "form" : form
        }
        return render(request, 'card/person_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = PersonForm(request.POST, request.FILES or None)
        if form.is_valid():
            person = form.save(commit = False)
            person.sourceCompany = request.user.profile.sourceCompany
            person.user = request.user
            person.sessionKey = request.session.session_key
            person.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'card/person_add.html', context)
        
class PersonAddInVesselView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Person")
        elementTagSub = "vesselPerson"
        form = PersonForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "form" : form
        }
        return render(request, 'card/person_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = PersonForm(request.POST, request.FILES or None)
        if form.is_valid():
            person = form.save(commit = False)
            person.sourceCompany = request.user.profile.sourceCompany
            person.user = request.user
            person.sessionKey = request.session.session_key
            person.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'card/person_add.html', context)
        
class PersonInDetailCompanyAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Company")
        elementTagSub = "companyPerson"
        form = PersonForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "form" : form
        }
        return render(request, 'card/person_add.html', context)
    
    def post(self, request, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        companyId = refererPath.replace("/card/company_update/","").replace("/","")
        form = PersonForm(request.POST, request.FILES or None)
        if form.is_valid():
            person = form.save(commit = False)
            person.sourceCompany = request.user.profile.sourceCompany
            person.user = request.user
            person.company = get_object_or_404(Company, id = companyId)
            person.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'card/person_add.html', context)
        
class PersonInDetailVesselAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Person")
        elementTagSub = "vesselPerson"
        form = PersonForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "form" : form
        }
        return render(request, 'card/person_add.html', context)
    
    def post(self, request, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        vesselId = refererPath.replace("/card/vessel_update/","").replace("/","")
        form = PersonForm(request.POST, request.FILES or None)
        if form.is_valid():
            person = form.save(commit = False)
            person.sourceCompany = request.user.profile.sourceCompany
            person.user = request.user
            person.vessel = get_object_or_404(Vessel, id = vesselId)
            person.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'card/person_add.html', context)

class PersonUpdateInCompanyView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Person Detail")
        elementTag = "company"
        elementTagSub = "companyPerson"
        elementTagId = id
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        person = get_object_or_404(Person, id = id)
        form = PersonForm(request.POST or None, request.FILES or None, instance = person)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "person" : person,
                "refererPath" : refererPath
        }
        return render(request, 'card/person_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        person = get_object_or_404(Person, id = id)
        company = person.company
        sourceCompany = person.sourceCompany
        form = PersonForm(request.POST, request.FILES or None, instance = person)
        if form.is_valid():
            person = form.save(commit = False)
            person.sourceCompany = sourceCompany
            person.company = company
            person.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'card/person_detail.html', context)

class PersonUpdateInVesselView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Person Detail")
        elementTagSub = "vesselPerson"
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        person = get_object_or_404(Person, id = id)
        form = PersonForm(request.POST or None, request.FILES or None, instance = person)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "form" : form,
                "person" : person,
                "refererPath" : refererPath
        }
        return render(request, 'card/person_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        person = get_object_or_404(Person, id = id)
        vessel = person.vessel
        sourceCompany = person.sourceCompany
        form = PersonForm(request.POST, request.FILES or None, instance = person)
        if form.is_valid():
            person = form.save(commit = False)
            person.sourceCompany = sourceCompany
            person.vessel = vessel
            person.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'card/person_detail.html', context)

class PersonDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Person")
        idList = list.split(",")
        for id in idList:
            print(int(id))
        context = {
                "tag": tag
        }
        return render(request, 'card/person_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:   
            person = get_object_or_404(Person, id = int(id))
            person.delete()
        return HttpResponse(status=204)

class BankInDetailCompanyAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Bank")
        elementTag = "company"
        elementTagSub = "companyBank"
        elementTagId = id
        form = BankForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form
        }
        return render(request, 'card/bank_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        companyId = refererPath.replace("/card/bank_update/","").replace("/","")
        form = BankForm(request.POST, request.FILES or None)
        if form.is_valid():
            bank = form.save(commit = False)
            bank.sourceCompany = request.user.profile.sourceCompany
            bank.user = request.user
            bank.company = get_object_or_404(Company, id = id)
            bank.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'card/bank_add.html', context)

class BankUpdateInCompanyView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Bank Detail")
        elementTag = "company"
        elementTagSub = "companyBank"
        elementTagId = id
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        bank = get_object_or_404(Bank, id = id)
        form = BankForm(request.POST or None, request.FILES or None, instance = bank)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "bank" : bank,
                "refererPath" : refererPath
        }
        return render(request, 'card/bank_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        bank = get_object_or_404(Bank, id = id)
        company = bank.company
        sourceCompany = bank.sourceCompany
        form = BankForm(request.POST, request.FILES or None, instance = bank)
        if form.is_valid():
            bank = form.save(commit = False)
            bank.sourceCompany = sourceCompany
            bank.company = company
            bank.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'card/bank_detail.html', context)

class BankDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Bank")
        idList = list.split(",")
        for id in idList:
            print(int(id))
        context = {
                "tag": tag
        }
        return render(request, 'card/bank_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:   
            bank = get_object_or_404(Bank, id = int(id))
            bank.delete()
        return HttpResponse(status=204)

class OwnerAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Owner")
        elementTagSub = "vesselOwner"
        form = OwnerForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "form" : form
        }
        return render(request, 'card/owner_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = OwnerForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            owner = form.save(commit = False)
            owner.sourceCompany = request.user.profile.sourceCompany
            owner.user = request.user
            owner.sessionKey = request.session.session_key
            owner.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'card/owner_add.html', context)

class OwnerInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Owner")
        elementTag = "owner"
        elementTagSub = "ownerPart"
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        vesselId = refererPath.replace("/card/vessel_update/","").replace("/","")
        vessel = get_object_or_404(Vessel, id = id)
        
        ownerForm = OwnerForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "vessel" : vessel,
                "ownerForm" : ownerForm
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'card/owner_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        vesselId = refererPath.replace("/card/vessel_update/","").replace("/","")
        
        vessel = Vessel.objects.get(id = id)
        
        ownerForm = OwnerForm(request.POST, request.FILES or None, user = request.user)
        if ownerForm.is_valid():
            owner = ownerForm.save(commit = False)
            owner.sourceCompany = request.user.profile.sourceCompany
            
            owner.user = request.user
            owner.vessel = vessel
            owner.save()
            
            owner.name = owner.ownerCompany.name
            owner.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "ownerForm" : ownerForm,
                    "vesselId" : vesselId
            }
            return render(request, 'card/owner_add_in_detail.html', context)

class OwnerDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Owner")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'card/owner_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            owner = get_object_or_404(Owner, id = int(id))
            owner.delete()
        return HttpResponse(status=204)
