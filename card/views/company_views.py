from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.db import IntegrityError
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
from ..utils import *
from account.models import SendInvoice

import pandas as pd
from validate_email import validate_email
import icu
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
    
def updateMikro(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "update_mikro",
            "message": message,
            "location" : location
        }
    )

def createMikro(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "create_mikro",
            "message": message,
            "location" : location
        }
    )

class CardDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Companies")
        elementTag = "company"
        elementTagSub = "companyPerson"

        #res = add.delay()
        #print(res.failed())
        
        context = {
                    "tag" : tag,
                    "elementTag": elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenilendiğinde doğrudan dashboard'a gider
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        #response = render(request, 'card/cards.html', context)
        #response.set_cookie("companyTab", "true")
        
        return render(request, 'card/company/companies.html', context)
       
class CompanyAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Company")
        elementTag = "company"
        elementTagSub = "companyPerson"
        elementTagId = "new"
        form = CompanyForm(request.POST or None, request.FILES or None, user=request.user)
        context = {
                "tag": tag,
                "elementTag": elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "form" : form
        }
        return render(request, 'card/company/company_add.html', context)
    
    def post(self, request, *args, **kwargs):
        elementTag = "company"
        elementTagSub = "companyPerson"
        elementTagId = "new"
        form = CompanyForm(request.POST, request.FILES or None, user = request.user)

        if form.is_valid():
            company = form.save()
            company.sourceCompany = request.user.profile.sourceCompany
            print(company.customerCheck)
            #####hata durumu#####
            if not company.customerCheck and not company.supplierCheck:
                data = {
                    "status":"secondary",
                    "icon":"triangle-exclamation",
                    "message":"At least one company role(customer or supplier) must be selected!"
                }
                
                sendAlert(data,"default")
                return HttpResponse(status=200)
            ####hata durumu-end#####

            company.lowerName = company.name.lower()
            company.save()
            
            sessionPersons = Person.objects.filter(sourceCompany = request.user.profile.sourceCompany,sessionKey = request.session.session_key, user = request.user, company = None)
            for sessionPerson in sessionPersons:
                sessionPerson.company = company
                sessionPerson.save()


            return HttpResponse(status=204)
        else:
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"triangle-exclamation",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
      
class CompanyUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Company Detail")
        elementTag = "company"
        elementTagSub = "companyPerson"
        elementTagId = id
        
        companies = Company.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        company = get_object_or_404(Company, sourceCompany = request.user.profile.sourceCompany,id = id)
        vessels = Vessel.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = company)
        
        if company.hesapKodu:
            cariKod = company.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
        
        data = {
                "cariKod" : cariKod
        }
        
        #check_mikro_connection.delay(data)
        
        #check_mikro_connection.delay(cariKod)
        
        # channel_layer = get_channel_layer()

        # async_to_sync(channel_layer.group_send)(
        #     'public_room',
        #     {
        #         "type": "check_mikro_connection",
        #         "cari_kod" : cariKod
        #     }
        # )
        
        form = CompanyForm(request.POST or None, request.FILES or None, instance = company, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "companies" : companies,
                "company" : company,
                "vessels" : vessels,
                "cariKod" : cariKod,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
        }
        return render(request, 'card/company/company_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "company"
        elementTagSub = "companyPerson"
        elementTagId = id
        
        company = get_object_or_404(Company, id = id)
        sourceCompany = request.user.profile.sourceCompany
        mikroGuid = company.mikroGuid
        lowerName = company.lowerName
        
        form = CompanyForm(request.POST, request.FILES or None, instance = company, user = request.user)
        
        if form.is_valid():
            company = form.save(commit = False)
            company.sourceCompany = sourceCompany
            
            
            #####hesap kodu check#####
            hesapKoduCheck = Company.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,hesapKodu = company.hesapKodu).exclude(id = company.id).first()
            if hesapKoduCheck and hesapKoduCheck.hesapKodu != "" and hesapKoduCheck.hesapKodu != None:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"The 'Hesap Kodu' field is already in use by another company!"
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=200)
            #####hesap kodu check-end#####
            
            company.mikroGuid = mikroGuid
            company.lowerName = lowerName
            company.save()
            
            sessionPersons = Person.objects.filter(sourceCompany = request.user.profile.sourceCompany,sessionKey = request.session.session_key, user = request.user, company = None)
            for sessionPerson in sessionPersons:
                sessionPerson.company = company
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
                "icon":"triangle-exclamation",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)

class CompanyDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Company")
        idList = list.split(",")
        for id in idList:
            print(int(id))
        context = {
                "tag": tag
        }
        return render(request, 'card/company/company_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        try:
            idList = list.split(",")
            for id in idList:   
                company = get_object_or_404(Company, id = int(id))
                company.delete()
            
            data = {
                "status":"success",
                "icon":"circle-check",
                "message":"Successfully removed! Please reload table."
            }
            
            sendAlert(data,"default")
            return HttpResponse(status=204)
        except IntegrityError as e:
            data = {
                "status":"secondary",
                "icon":"triangle-exclamation",
                "message":"This object is still referenced from another objects!"
            }
            
            sendAlert(data,"default")
            return HttpResponse(status=200)
        
class CompanyLogoView(LoginRequiredMixin, View):     
    def get(self, request, id, *args, **kwargs):
        company = get_object_or_404(Company, id = id)
        src = company.logo.url
        context = {
                "src" : src
        }

        return render(request, "card/company/company-logo.html", context)
        
class CompanyFilterExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Company Excel")
        
        elementTag = "companyExcel"
        elementTagSub = "companyPartExcel"

        countries = Country.objects.select_related().filter().order_by("international_formal_name")
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "countries" : countries,
                "sessionKey" : request.session.session_key
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'card/company/company_excel.html', context)       

class CompanyExportExcelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "card", "company", "documents")
        
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
        if request.GET.get("c") == "true":
            customerCheck = True
        else:
            customerCheck = False
        
        if request.GET.get("s") == "true":
            supplierCheck = True
        else:
            supplierCheck = False
            
        countryId = request.GET.get("co")
        cityId = request.GET.get("ci")

        companies = Company.objects.select_related("country","city").filter(
            Q(sourceCompany = request.user.profile.sourceCompany) &
            (Q(customerCheck = customerCheck) | Q(supplierCheck = supplierCheck))
        ).order_by("name").distinct()

        if countryId != "0":
            companies = companies.filter(country = int(countryId)).order_by("name")

        if cityId != "0":
            companies = companies.filter(city = int(cityId)).order_by("name")

        data = {
            "Name": [],
            "Cari Kod": [],
            "Type": [],
            "Country": [],
            "City": [],
            "Address": [],
            "Phone": [],
            "Email": [],
            "Vat Office": [],
            "Vat No": []
            
        }
        
        channel_layer = get_channel_layer()
        
        seq = 0
        for company in companies:
            async_to_sync(channel_layer.group_send)(
                'private_' + str(request.user.id),
                {
                    "type": "send_percent",
                    "message": seq,
                    "location" : "company_excel",
                    "totalCount" : len(companies),
                    "ready" : "false"
                }
            )
            
            if company.country:
                countryName = company.country.international_formal_name
            else:
                countryName = ""
                
            if company.city:
                cityName = company.city.name
            else:
                cityName = ""

            role = ""

            if company.customerCheck:
                role = "Customer"

            if company.supplierCheck:
                if company.customerCheck:
                    role = f"{role}, Supplier"
                else:
                    role = "Supplier"
                
            data["Name"].append(company.name)
            data["Cari Kod"].append(company.hesapKodu)
            data["Type"].append(role)
            data["Country"].append(countryName)
            data["City"].append(cityName)
            data["Address"].append(company.address)
            data["Phone"].append(company.phone1)
            data["Email"].append(company.email)
            data["Vat Office"].append(company.vatOffice)
            data["Vat No"].append(company.vatNo)
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/company-list.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Quotation', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        if companies:
            companiesCount = len(companies)
        else:
            companiesCount = 0
        async_to_sync(channel_layer.group_send)(
            'private_' + str(request.user.id),
            {
                "type": "send_percent",
                "message": seq,
                "location" : "company_excel",
                "totalCount" : companiesCount,
                "ready" : "true"
            }
        )
        
        return HttpResponse(status=204)

class CompanyDownloadExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/card/company/documents/company-list.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'
        
        return response


#####MİKRO#####
class CompanyUpdateFromMikroView(LoginRequiredMixin, View):
    def get(self, request, id, hesapKodu, *args, **kwargs):
        tag = _("Get updates")
        
        elementTag = "companyUpdateFrom"
        elementTagSub = "companyPartInUpdateFrom"
        elementTagId = id
        
        company = Company.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,id = id).first()
        
        if company.hesapKodu:
            cariKod = company.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "cariKod" : cariKod
        }
        return render(request, 'card/company/get_updates_from_mikro.html', context)
    
    def post(self, request, id, hesapKodu, *args, **kwargs):
        channel_layer = get_channel_layer()
        
        company = get_object_or_404(Company, sourceCompany = request.user.profile.sourceCompany,id = id)
        cariKod = company.hesapKodu
        
        data = {"cariKod":cariKod,
                "cariName":company.name,
                "companyId":id,
                "mikroDBName":request.user.profile.sourceCompany.mikroDBName
                        }
            
        updateMikro(data,"update_from_mikro_company")
        
        return HttpResponse(status=204)
    
class CompanyUpdateToMikroView(LoginRequiredMixin, View):
    def get(self, request, id, hesapKodu, *args, **kwargs):
        tag = _("Get updates")
        
        elementTag = "companyUpdateTo"
        elementTagSub = "companyPartInUpdateTo"
        elementTagId = id
        
        company = get_object_or_404(Company, id = id)
        
        if company.hesapKodu:
            cariKod = company.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "cariKod" : cariKod
        }
        return render(request, 'card/company/send_updates_to_mikro.html', context)
    
    def post(self, request, id, hesapKodu, *args, **kwargs):
        channel_layer = get_channel_layer()
        
        company = get_object_or_404(Company, id = id)
        cariKod = company.hesapKodu

        countryTR = Country.objects.select_related().filter(id = 205).first()

        address={}

        if company.country == countryTR:
            if company.city:
                address["city"] = locale_upper(company.city.name, 'tr_TR')
                if isinstance(address["city"], icu.UnicodeString):
                    address["city"] = str(address["city"])
            else:
                address["city"] = ""
        else:
            address["city"] = ""

        if company.country:
            address["country"] = locale_upper(company.country.formal_name, 'tr_TR')
            if isinstance(address["country"], icu.UnicodeString):
                address["country"] = str(address["country"])
        else:
            address["country"] = ""

        if company.address:
            address["address"] = company.address
        else:
            address["address"] = ""
        
        data = {"cariKod":cariKod,
                "cariName":company.name,
                "companyId":id,
                "adres":address,
                "mikroDBName":request.user.profile.sourceCompany.mikroDBName
                        }
            
        updateMikro(data,"update_to_mikro_company")
        
        return HttpResponse(status=204)

class CompanyMatchWithMikroView(LoginRequiredMixin, View):
    def get(self, request, id, hesapKodu, *args, **kwargs):
        tag = _("Get updates")
        
        elementTag = "companyMatchWith"
        elementTagSub = "companyPartInMatchWith"
        elementTagId = id
        
        company = Company.objects.select_related().filter(id = id).first()
        
        if company.hesapKodu:
            cariKod = company.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "cariKod" : cariKod
        }
        return render(request, 'card/company/match_with_mikro.html', context)
    
    def post(self, request, id, hesapKodu, *args, **kwargs):
        channel_layer = get_channel_layer()
        
        company = Company.objects.select_related().filter(id = id).first()
        cariKod = company.hesapKodu
        
        data = {
                "type":"company",
                "cariKod":cariKod,
                "cariName":company.name,
                "companyId":id,
                "mikroDBName":request.user.profile.sourceCompany.mikroDBName
                }
            
        matchMikro(data,"match_mikro")
        
        return HttpResponse(status=204)

class CompanyUnmatchWithMikroView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Get updates")
        
        elementTag = "companyUnmatchWith"
        elementTagSub = "companyPartInUnmatchWith"
        elementTagId = id
        
        company = Company.objects.select_related().filter(id = id).first()
        
        if company.hesapKodu:
            cariKod = company.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "cariKod" : cariKod
        }
        return render(request, 'card/company/unmatch_with_mikro.html', context)
    
    def post(self, request, id, *args, **kwargs):
        channel_layer = get_channel_layer()
        
        company = Company.objects.select_related().filter(id = id).first()
        cariKod = company.hesapKodu
        
        data = {
                "type":"company",
                "cariName":company.name,
                "companyId":id,
                "mikroDBName":request.user.profile.sourceCompany.mikroDBName
                }
            
        matchMikro(data,"unmatch_mikro")
        
        return HttpResponse(status=204)

class CompanyCreateMikroView(LoginRequiredMixin, View):
    def get(self, request, id, hesapKodu, *args, **kwargs):
        tag = _("Get updates")
        
        elementTag = "companyCreateMikro"
        elementTagSub = "companyPartCreateMikro"
        elementTagId = id
        
        company = get_object_or_404(Company, id = id)
        
        if company.hesapKodu:
            cariKod = company.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "cariKod" : cariKod
        }
        return render(request, 'card/company/create_mikro_company.html', context)
    
    def post(self, request, id, hesapKodu, *args, **kwargs):
        company = get_object_or_404(Company, id = id)
        
        countryTR = Country.objects.select_related().filter(id = 205).first()
        
        if company.role["customer"] == True:
            cariBasKod = "120"
        else:
            cariBasKod = "320"
        
        if company.country == countryTR:
            cariOrtaKod = "01"
        else:
            cariOrtaKod = "02"
        
        address={}

        if company.country == countryTR:
            if company.city:
                address["city"] = locale_upper(company.city.name, 'tr_TR')
                if isinstance(address["city"], icu.UnicodeString):
                    address["city"] = str(address["city"])
            else:
                address["city"] = ""
        else:
            address["city"] = ""

        if company.country:
            address["country"] = locale_upper(company.country.formal_name, 'tr_TR')
            if isinstance(address["country"], icu.UnicodeString):
                address["country"] = str(address["country"])
        else:
            address["country"] = ""

        if company.address:
            address["address"] = company.address
        else:
            address["address"] = ""

            
        
        

        data = {
            "type":"company",
            "cariBasKod":cariBasKod,
            "cariOrtaKod":cariOrtaKod,
            "cariName":company.name,
            "companyId":id,
            "adres":address,
            "mikroDBName":request.user.profile.sourceCompany.mikroDBName
                        }
            
        createMikro(data,"create_mikro")
        
        return HttpResponse(status=204)


#####MİKRO-end#####

