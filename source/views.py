from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
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
import json

from .forms import *

class BankDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Bank")
        elementTag = "bank"
        elementTagSub = "bankPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'source/banks.html', context)

class BankAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Bank")
        elementTag = "bank"
        elementTagSub = "bankPart"
        elementTagId = "new"
        
        form = BankForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'source/bank_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = BankForm(request.POST, request.FILES or None, user = request.user)
        
        if form.is_valid():
            bank = form.save(commit = False)
            bank.company = request.user.profile.sourceCompany
            bank.user = request.user
            bank.save()

            return HttpResponse(status=204)
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'source/bank_add.html', context)
 
 
class BankUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Bank Detail")
        elementTag = "bank"
        elementTagSub = "bankPerson"
        elementTagId = id
        
        bank = get_object_or_404(Bank, id = id)
        payments = bank.payment_source_bank.order_by("-id").all()
        
        form = BankForm(request.POST or None, request.FILES or None, instance = bank, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "bank" : bank,
                "payments" : payments,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
        }
        return render(request, 'source/bank_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        bank = get_object_or_404(Bank, id = id)
        user = bank.user
        company = bank.company
        company = bank.company
        
        form = BankForm(request.POST, request.FILES or None, instance = bank, user = request.user)
        if form.is_valid():
            bank = form.save(commit = False)
            bank.company = company
            bank.company = company
            bank.user = user
            bank.save()
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)