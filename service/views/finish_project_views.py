from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage, send_mail
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa
from django.template.loader import get_template
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync 

from ..forms import *
from ..pdfs.offer_pdfs import *
from ..pdfs.active_project_pdfs import *
from ..pdfs.finish_project_pdfs import *

from source.models import Company as SourceCompany

import pandas as pd
import json
import random
import string
from datetime import datetime

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


class FinishProjectDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Finish Projects")
        elementTag = "finishProject"
        elementTagSub = "finishProjectPart"

        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/finish_project/finish_projects.html', context)
    
class FinishProjectUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Finish Project Detail")
        elementTag = "finishProject"
        elementTagSub = "finishProjectPart"
        elementTagId = id
        
        finishProjects = Offer.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        finishProject = get_object_or_404(Offer, id = id)
        
        images = OfferImage.objects.filter(offer = finishProject)
        notes = OfferNote.objects.select_related("user").filter(sourceCompany = request.user.profile.sourceCompany,offer = finishProject)
        
        #parts = RequestPart.objects.filter(theRequest = requestt)
        
        #addParts = Part.objects.filter(maker = requestt.maker, type = requestt.makerType)
        #partsLength = len(addParts)
        
        form = OfferForm(request.POST or None, request.FILES or None, instance = finishProject, user = request.user)
        imageForm = OfferImageForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "imageForm" : imageForm,
                "finishProjects" : finishProjects,
                "finishProject" : finishProject,
                "images" : images,
                "notes" : notes,
                #"parts" : parts,
                #"addParts" : addParts,
                #"partsLength" : partsLength,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/finish_project/finish_project_detail.html', context)

    def post(self, request, id, *args, **kwargs):
        finishProject = get_object_or_404(Offer, id = id)

        form = FinishedOfferForm(request.POST, request.FILES or None, instance = finishProject, user = request.user)
        if form.is_valid():
            finishProject = form.save(commit = False)
            finishProject.save()

            finishProjectPdf(finishProject,request.user.profile.sourceCompany)
            finishProjectPdfWithoutPrice(finishProject,request.user.profile.sourceCompany)
        else:
            print(form.errors)
            return HttpResponse(status=404)
                
        return HttpResponse(status=204)
    
class FinishProjectPdfView(LoginRequiredMixin, View):
    def get(self, request, id, type, *args, **kwargs):
        tag = _("Finish Project PDF")
        
        elementTag = "finishProject"
        elementTagSub = "finishProjectPart"
        elementTagId = str(id) + "-pdf"
        
        finishProject = Offer.objects.get(id = id)
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        if type == "normal":
            src = "/media/docs/" + str(request.user.profile.sourceCompany.id) + "/service/finish_project/documents/" + str(finishProject.offerNo) + ".pdf?v=" + str(version)
        elif type == "wop":
            src = "/media/docs/" + str(request.user.profile.sourceCompany.id) + "/service/finish_project/documents/" + str(finishProject.offerNo) + "-without-price.pdf?v=" + str(version)
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "finishProject" : finishProject,
                "version" : version,
                "src" : src
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/finish_project/finish_project_pdf.html', context)
    
class FinishProjectImageView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        elementTag = "finishProject"
        elementTagSub = "finishProjectPart"
        elementTagId = id
        
        finishProjects = Offer.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        finishProject = get_object_or_404(Offer, id = id)
        
        images = OfferImage.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = finishProject)
        
        imageForm = OfferImageForm(request.POST or None, request.FILES or None)
        context = {
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "imageForm" : imageForm,
                "finishProjects" : finishProjects,
                "finishProject" : finishProject,
                "images" : images,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/finish_project/finish_project_image.html', context)       
class FinishProjectImageAddView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        finishProject = get_object_or_404(Offer, id = id)
        
        image = OfferImage.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            offer = finishProject,
            image = request.FILES.get("image")
        )
        
        image.save()
            
        return HttpResponse(status=204)
    
class FinishProjectImageDeleteView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        
        image = OfferImage.objects.get(id = id)
        image.delete()
            
        return HttpResponse(status=204)

class FinishProjectDocumentView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        elementTag = "finishProject"
        elementTagSub = "finishProjectPart"
        elementTagId = id
        
        finishProjects = Offer.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        finishProject = Offer.objects.filter(id = id).first()
        
        finishProjectDocuments = OfferDocument.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = finishProject)

        documents = OfferDocument.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = finishProject)
        
        finishProjectDocumentForm = OfferDocumentForm(request.POST or None, request.FILES or None)
        context = {
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "finishProjectDocumentForm" : finishProjectDocumentForm,
                "finishProjects" : finishProjects,
                "finishProject" : finishProject,
                "finishProjectDocuments" : finishProjectDocuments,
                "documents" : documents,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/finish_project/finish_project_document.html', context)

class FinishProjectDocumentAddView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        finishProject = Offer.objects.filter(id=id).first()
        pageLoad(request,20,100,"false")
        finishProjectDocument = OfferDocument.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            sessionKey = request.session.session_key,
            offer = finishProject,
            file = request.FILES.get("file")
        )
        pageLoad(request,90,100,"false")
        finishProjectDocument.save()
        pageLoad(request,100,100,"true")
        return HttpResponse(status=204)

class FinishProjectDocumentDeleteView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        
        finishProjectDocument = OfferDocument.objects.get(id = id)
        finishProjectDocument.delete()
            
        return HttpResponse(status=204)
    
class FinishProjectDocumentPdfView(LoginRequiredMixin, View):
    def get(self, request, id, name, *args, **kwargs):
        tag = _("Finish Project Document PDF")
        
        elementTag = "finishProject"
        elementTagSub = "finishProjectPart"
        elementTagId = str(id) + "-pdf"
        
        pageLoad(request,0,100,"false")
        
        finishProjectDocument = OfferDocument.objects.get(id = id, name = name)
        finishProject = finishProjectDocument.offer
        pageLoad(request,50,100,"false")
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "finishProjectDocument" : finishProjectDocument,
                "finishProject" : finishProject,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'service/finish_project/finish_project_document_pdf.html', context)

class FinishProjectNoteAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Note")
        
        finishProject = Offer.objects.select_related().filter(id = id).first()
        newNote = OfferNote.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            title = request.GET.get("title"),
            text  =request.GET.get("text"),
            user = request.user,
            offer = finishProject
        )
        
        newNote.save()
        
        if request.user.first_name:
            firstName = request.user.first_name
        else:
            firstName = ""
            
        if request.user.last_name:
            lastName = request.user.last_name
        else:
            lastName = ""
        
        note = {
            "id" : newNote.id,
            "title" : newNote.title,
            "text" : newNote.text,
            "date" : newNote.created_date.strftime("%d.%m.%Y"),
            "user" : firstName + " " + lastName,
            "finishProjectId" : finishProject.id
        }
        
        sendProcess(request,note,"finishProject_note_add")
        
        context = {
                "tag": tag
        }
        return HttpResponse(status=204)

class FinishProjectNoteDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Delete Note")
        
        exNote = OfferNote.objects.select_related().filter(id = int(request.GET.get("note"))).first()
        exNoteId = exNote.id
        note = {
            "id" : exNoteId
        }
        
        exNote.delete()
        
        sendProcess(request,note,"finishProject_note_delete")
        
        context = {
                "tag": tag
        }
        return HttpResponse(status=204)


class FinishProjectPdfView(LoginRequiredMixin, View):
    def get(self, request, id, type, *args, **kwargs):
        tag = _("Finish Project PDF")
        
        elementTag = "finishProject"
        elementTagSub = "finishProjectPart"
        elementTagId = str(id) + "-pdf"
        
        finishProject = Offer.objects.get(id = id)
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        if type == "normal":
            src = "/media/docs/" + str(request.user.profile.sourceCompany.id) + "/service/finish_project/documents/" + str(finishProject.offerNo) + ".pdf?v=" + str(version)
        elif type == "wop":
            src = "/media/docs/" + str(request.user.profile.sourceCompany.id) + "/service/finish_project/documents/" + str(finishProject.offerNo) + "-without-price.pdf?v=" + str(version)
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "finishProject" : finishProject,
                "version" : version,
                "src" : src
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/finish_project/finish_project_pdf.html', context)
 