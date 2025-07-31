from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.translation import gettext_lazy as _
# Create your views here.
from django.views import View
from urllib.parse import urlparse
from django.contrib import messages
from django.db.models import Prefetch

from ..forms import *

from sale.models import RequestPart, InquiryPart, QuotationPart, PurchaseOrderPart
from account.models import SendInvoicePart, ProformaInvoicePart, IncomingInvoicePart
from service.models import OfferPart

import pandas as pd

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

class ExpenseDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Expenses")
        elementTag = "expense"
        elementTagSub = "expensePart"
        
        expenses = Expense.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "expenses" : expenses
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/expenses.html', context)

class ExpenseAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Expense")
        elementTag = "expense"
        elementTagSub = "expensePart"
        elementTagId = "new"
        
        form = ExpenseForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/expense_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = ExpenseForm(request.POST, request.FILES or None)
        if form.is_valid():
            expense = form.save()
            expense.sourceCompany = request.user.profile.sourceCompany
            expense.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'data/expense_add.html', context)
        
class ExpenseUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Expense Detail")
        elementTag = "expense"
        elementTagSub = "expensePart"
        elementTagId = id
        
        expenses = Expense.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        expense = get_object_or_404(Expense, id = id)
        form = ExpenseForm(request.POST or None, request.FILES or None, instance = expense)
        context = {
                "tag": tag,
                "form" : form,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "expenses" : expenses,
                "expense" : expense
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/expense_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        expense = get_object_or_404(Expense, id = id)
        sourceCompany = expense.sourceCompany
        form = ExpenseForm(request.POST, request.FILES or None, instance = expense)
        if form.is_valid():
            expense = form.save(commit = False)
            expense.sourceCompany = sourceCompany
            expense.save()
            
            return HttpResponse(status=204)
            
        else:
            return HttpResponse(status=404)
    
class ExpenseDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Expense")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/expense_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            expense = get_object_or_404(Expense, id = int(id))
            expense.delete()
        return HttpResponse(status=204)