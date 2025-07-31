from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.http.response import HttpResponse
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .forms import *
from hr.models import TheCompany
from user.forms import UserLoginForm, ProfileForm, UserInfoForm, CustomPasswordResetForm
from note.models import Note
from sale.models import Request, Quotation, OrderConfirmation
from card.models import Company
from data.models import Part
from source.models import Company as SourceCompany

from django.utils import timezone
from django.utils.formats import date_format
from datetime import date, timedelta, datetime
from urllib.parse import urlparse

from forex_python.converter import CurrencyRates
import requests as rs
import xmltodict
import json
import pyodbc
import random
import string

import subprocess
from django.core import serializers
from .models import Position

from administration.models import AccessAuthorization as AccessAuth
from administration.models import DataAuthorization as DataAuth
# Create your views here.

import telnetlib


from .tasks import *
from card.models import Country
from service.models import Offer
from notifications.models import Notify
from account.models import SendInvoice,IncomingInvoice, Payment

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

class DashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Dashboard")
        elementTag = "dashboard"
        
        
        
        # HOST = "192.168.2.7"
        # PORT = 1433  # Varsayılan telnet portu
        # TIMEOUT = 10  # Bağlantı zaman aşımı süresi (saniye)
        
        # try:
        #     # Telnet bağlantısını aç
        #     with telnetlib.Telnet(HOST, PORT, TIMEOUT) as tn:

        #         # Sunucudan hoşgeldiniz mesajını oku (örnek)
        #         welcome_message = tn.read_some().decode('ascii')
        #         print("Bağlantı başarılı:", welcome_message)

        #         # Bağlantıyı kapat (with bloğu otomatik olarak kapatır)
        # except Exception as e:
        #     print(f"Bağlantı hatası: {e}")
        
        
        notifications = Notify.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany).order_by("-id")
        
        #country = Country.objects.get(international_formal_name = "Türkiye")
        
        ##### Doviz Guncelleme #####
        trl = Currency.objects.get(code = "TRY")
        usd = Currency.objects.get(code = "USD")
        eur = Currency.objects.get(code = "EUR")
        gbp = Currency.objects.get(code = "GBP")
        qar = Currency.objects.get(code = "QAR")
        rub = Currency.objects.get(code = "RUB")
        jpy = Currency.objects.get(code = "JPY")
        
        # if rs.get("https://www.tcmb.gov.tr/kurlar/today.xml").status_code == 200:
        #     ratesSource = rs.get("https://www.tcmb.gov.tr/kurlar/today.xml").content
        #     rates = xmltodict.parse(ratesSource)
        #     jsonRates = json.dumps(rates)
        #     with open("card/fixtures/exchange-rates.json", "w") as f:
        #         f.write(jsonRates)
            
        #     ratesDate = rates["Tarih_Date"]["@Tarih"]
        #     rates = rates["Tarih_Date"]["Currency"]
            
        #     rates_usd = next((rate for rate in rates if rate['@Kod'] == 'USD'), None)
        #     rates_eur = next((rate for rate in rates if rate['@Kod'] == 'EUR'), None)
        #     rates_gbp = next((rate for rate in rates if rate['@Kod'] == 'GBP'), None)
        #     rates_qar = next((rate for rate in rates if rate['@Kod'] == 'QAR'), None)
        #     rates_rub = next((rate for rate in rates if rate['@Kod'] == 'RUB'), None)
        #     rates_jpy = next((rate for rate in rates if rate['@Kod'] == 'JPY'), None)
            
        #     trl.baseCurrency = "try"
        #     trl.forexBuying = 1.00
        #     trl.forexSelling = 1.00
        #     trl.banknoteBuying = 1.00
        #     trl.banknoteBuying = 1.00
        #     trl.rateUSD = rates_usd["ForexBuying"]
        #     trl.rateOther = None
        #     trl.rateDate = timezone.now().date()
        #     trl.tcmbRateDate = ratesDate
        #     trl.save()
            
        #     usd.baseCurrency = "try"
        #     usd.forexBuying = rates_usd["ForexBuying"]
        #     usd.forexSelling = rates_usd["ForexSelling"]
        #     usd.banknoteBuying = rates_usd["BanknoteBuying"]
        #     usd.banknoteBuying = rates_usd["BanknoteSelling"]
        #     usd.rateUSD = None
        #     usd.rateOther = None
        #     usd.rateDate = timezone.now().date()
        #     usd.tcmbRateDate = ratesDate
        #     usd.save()
            
        #     eur.baseCurrency = "try"
        #     eur.forexBuying = rates_eur["ForexBuying"]
        #     eur.forexSelling = rates_eur["ForexSelling"]
        #     eur.banknoteBuying = rates_eur["BanknoteBuying"]
        #     eur.banknoteBuying = rates_eur["BanknoteSelling"]
        #     eur.rateUSD = None
        #     eur.rateOther = rates_eur["CrossRateOther"]
        #     eur.rateDate = timezone.now().date()
        #     eur.tcmbRateDate = ratesDate
        #     eur.save()
            
        #     gbp.baseCurrency = "try"
        #     gbp.forexBuying = rates_gbp["ForexBuying"]
        #     gbp.forexSelling = rates_gbp["ForexSelling"]
        #     gbp.banknoteBuying = rates_gbp["BanknoteBuying"]
        #     gbp.banknoteBuying = rates_gbp["BanknoteSelling"]
        #     gbp.rateUSD = None
        #     gbp.rateOther = rates_gbp["CrossRateOther"]
        #     gbp.rateDate = timezone.now().date()
        #     gbp.tcmbRateDate = ratesDate
        #     gbp.save()
            
        #     qar.baseCurrency = "try"
        #     qar.forexBuying = rates_qar["ForexBuying"]
        #     qar.forexSelling = rates_qar["ForexSelling"]
        #     qar.banknoteBuying = rates_qar["BanknoteBuying"]
        #     qar.banknoteBuying = rates_qar["BanknoteSelling"]
        #     qar.rateUSD = rates_qar["CrossRateUSD"]
        #     qar.rateOther = None
        #     qar.rateDate = timezone.now().date()
        #     qar.tcmbRateDate = ratesDate
        #     qar.save()
            
        #     rub.baseCurrency = "try"
        #     rub.forexBuying = rates_rub["ForexBuying"]
        #     rub.forexSelling = rates_rub["ForexSelling"]
        #     rub.banknoteBuying = rates_rub["BanknoteBuying"]
        #     rub.banknoteBuying = rates_rub["BanknoteSelling"]
        #     rub.rateUSD = rates_rub["CrossRateUSD"]
        #     rub.rateOther = None
        #     rub.rateDate = timezone.now().date()
        #     rub.tcmbRateDate = ratesDate
        #     rub.save()
            
        #     jpy.baseCurrency = "try"
        #     jpy.forexBuying = round(float(rates_jpy["ForexBuying"]) / 100,4)
        #     jpy.forexSelling = round(float(rates_jpy["ForexSelling"]) / 100,4)
        #     jpy.banknoteBuying = round(float(rates_jpy["BanknoteBuying"]) / 100,4)
        #     jpy.banknoteBuying = round(float(rates_jpy["BanknoteSelling"]) / 100,4)
        #     jpy.rateUSD = rates_jpy["CrossRateUSD"]
        #     jpy.rateOther = None
        #     jpy.rateDate = timezone.now().date()
        #     jpy.tcmbRateDate = ratesDate
        #     jpy.save()
        
        ##### Doviz Guncelleme-end #####
        
        # user = User.objects.get(username = "burcutaspinar")
        # password = User.objects.make_random_password()
        # user.set_password(password)
        # user.save()
        # print(password)
        
        #cnxn = pyodbc.connect('Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2')
        
        #dd = rs.get("http://api.exchangeratesapi.io/v1/latest?access_key=13be3e57aa6c82fba97fa7f0997db7b9&base=TRY").json()

        ####verileri json'a aktarma komutu###
        # positions = Position.objects.filter()
        # with open(r'position-new-2.json', "w") as out:
        #     mast_point = serializers.serialize("json", positions)
        #     out.write(mast_point)
        ####verileri json'a aktarma komutu-end###
        
        #get app version
        try:
            git_version = subprocess.check_output(["git", "describe", "--tags"]).strip()
            michoAppVersion = git_version.decode("utf-8")[:7]
        except Exception:
            michoAppVersion = "N/A"
        
        
        currentMonth = datetime.today().month
        currentMonthName = date_format(datetime.today(), "F")
        
        # #user'a group ekleme  
        # user = request.user
        # group = Group.objects.get(name="sales")
        
        # user.groups.add(group)
        # user.save()
        # #user'a group ekleme-end
                
        # carts = Cart.objects.filter()
        # print(carts[0].cartpart_set.select_related('part')[0].part.partNo)
        
        # cartParts = CartPart.objects.filter()
        # for cartPart in cartParts:
        #     print(cartPart.part)
        
        # try:
        #     c = CurrencyRates()
            
        #     exchange = {"usd" : round(c.get_rate('USD', 'TRY'),4),
        #                 "eur" : round(c.get_rate('EUR', 'TRY'),4),
        #                 "gbp" : round(c.get_rate('GBP', 'TRY'),4),
        #                 "aud" : round(c.get_rate('AUD', 'TRY'),4),
        #                 "cad" : round(c.get_rate('CAD', 'TRY'),4),
        #                 "jpy" : round(c.get_rate('JPY', 'TRY'),4)
        #                 }
        # except:
        #     exchange = {"usd" : 0.0000,
        #                 "eur" : 0.0000,
        #                 "gbp" : 0.0000,
        #                 "aud" : 0.0000,
        #                 "cad" : 0.0000,
        #                 "jpy" : 0.0000
        #                 }
            
        # exchange = {"usd" : 0.0000,
        #                 "eur" : 0.0000,
        #                 "gbp" : 0.0000,
        #                 "aud" : 0.0000,
        #                 "cad" : 0.0000,
        #                 "jpy" : 0.0000
        #                 }
        
       
        requests = Request.objects.select_related("customer").filter(sourceCompany = request.user.profile.sourceCompany).order_by("-created_date")
        emptyLineRequestCounter = 4 - len(requests)
        
        approvalClass = ""
        
        if request.user.profile.positionType:
            if request.user.profile.positionType.name == "Sales Assistant":
                approvalQuotations = Quotation.objects.select_related().filter(
                    sourceCompany = request.user.profile.sourceCompany,
                    approval = "sent", approvalClass__in = ["assistant"]
                )
            elif request.user.profile.positionType.name == "Sales Specialist":
                approvalQuotations = Quotation.objects.select_related().filter(
                    sourceCompany = request.user.profile.sourceCompany,
                    approval = "sent", approvalClass__in = ["assistant", "specialist"]
                )
            elif request.user.profile.positionType.name == "Sales Executivor":
                approvalQuotations = Quotation.objects.select_related().filter(
                    sourceCompany = request.user.profile.sourceCompany,
                    approval = "sent", approvalClass__in = ["assistant", "specialist", "executivor"]
                )
            elif request.user.profile.positionType.name == "Sales Director":
                approvalQuotations = Quotation.objects.select_related().filter(
                    sourceCompany = request.user.profile.sourceCompany,
                    approval = "sent", approvalClass__in = ["assistant", "specialist", "executivor", "director"]
                )
            elif request.user.profile.positionType.name == "Managing Director":
                approvalQuotations = Quotation.objects.select_related().filter(
                    sourceCompany = request.user.profile.sourceCompany,
                    approval = "sent", approvalClass__in = ["assistant", "specialist", "executivor", "director", "generalManager"]
                )
            else:
                approvalQuotations = []
        else:
                approvalQuotations = []
        
        emptyLineMACounter = 4 - len(approvalQuotations)
        
        approvalInvoices = OrderConfirmation.objects.select_related("quotation__inquiry__theRequest","quotation__inquiry__theRequest__customer").filter(sourceCompany = request.user.profile.sourceCompany,status = "collected")
        emptyLineOCCounter = 4 - len(approvalInvoices)
        
        notes = Note.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,user = request.user)
        
        isUserManager = request.user.groups.filter(name="manager").exists()
        userGroups = []
        
        for group in Group.objects.filter():
            userGroups.append(group.name)
        
        sourceCompanyList = request.user.profile.sourceCompanyList.all()
        sourceCompanyIdList = [sourceCompany.id for sourceCompany in sourceCompanyList]
        
        sourceCompanies = SourceCompany.objects.filter(id__in = sourceCompanyIdList)[:7]
        
        offers = Offer.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        #quotations = Quotation.objects.select_related("inquiry__theRequest__customer","inquiry__theRequest__project").filter().order_by("-id")[:10]
        
        quotations = request.user.quotation_user.select_related("inquiry__theRequest__customer","inquiry__theRequest__vessel").filter(
            sourceCompany = request.user.profile.sourceCompany
        ).order_by("-id")
        
        orderConfirmations = request.user.order_confirmation_user.select_related("quotation").filter(
            sourceCompany = request.user.profile.sourceCompany
        ).order_by("-id")
        
        sendInvoices = SendInvoice.objects.select_related().filter(
            sourceCompany = request.user.profile.sourceCompany,
            paymentDate__lt = timezone.now().date(),
            paidPrice = 0
        ).order_by("paymentDate")
        
        incomingInvoices = IncomingInvoice.objects.select_related().filter(
            sourceCompany = request.user.profile.sourceCompany,
            paymentDate__lt = timezone.now().date(),
            paidPrice = 0
        ).order_by("paymentDate")
        
        userAccesses = request.user.profile.accessAuth.all()
        userAccessesList = [userAccess.code for userAccess in userAccesses]
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #print(request.META.get('HTTP_COOKIE'))
        
        #print(request.COOKIES)
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "notifications" : notifications,
                    "michoAppVersion"  :michoAppVersion,
                    "currentMonthName" : currentMonthName,
                    "usd" : usd,
                    "eur" : eur,
                    "gbp" : gbp,
                    "qar" : qar,
                    "rub" : rub,
                    "jpy" : jpy,
                    #"ratesDate" : ratesDate,
                    "requests" : requests,
                    "emptyLineRequestCounter" : emptyLineRequestCounter,
                    "approvalQuotations" : approvalQuotations,
                    "emptyLineMACounter" : emptyLineMACounter,
                    "approvalInvoices" : approvalInvoices,
                    "emptyLineOCCounter" : emptyLineOCCounter,
                    "notes" : notes,
                    "isUserManager" : isUserManager,
                    "userGroups" : userGroups,
                    "sourceCompanies" : sourceCompanies,
                    "offers" : offers,
                    "quotations" : quotations,
                    "orderConfirmations"  :orderConfirmations,
                    "sendInvoices" : sendInvoices,
                    "incomingInvoices" : incomingInvoices,
                    "userAccessesList" : userAccessesList,
                    "version" : version,
                    "user" : request.user
        }
        
        #response = render(request, 'user/dashboard2.html', context)
        #response.set_cookie('dataflair', 'Hello this is your Cookies', max_age = None)
        
        return render(request, 'user/dashboard2.html', context)



class LandingPageView(LoginView):
    template_name = 'landing_page.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = form.cleaned_data['remember_me']
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super(LandingPageView, self).form_valid(form)


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_form = UserInfoForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, 'user/profile_page.html', context)

    def post(self, request, *args, **kwargs):
        user_form = UserInfoForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # to prevent refresh that sends post data again.
            return redirect("profile_page")
        else:
            context = {
                'user_form': user_form,
                'profile_form': profile_form
            }
            return render(request, 'user/profile_page.html', context)


        
class CustomPasswordResetView(PasswordResetView):
    html_email_template_name = 'registration/password_reset_email.html'
    form_class = CustomPasswordResetForm

    def __init__(self, **kwargs):
        self.extra_email_context = {'the_company': TheCompany.objects.get(id=1)}
        super().__init__(**kwargs)

class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, username, *args, **kwargs):
        tag = _("Requests")
        elementTag = "request"
        elementTagSub = "requestPart"
        elementTagId = username

        profile = request.user.profile
        print(profile.user.first_name)

        form = UserProfileForm(request.POST or None, request.FILES or None, instance = profile)
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "elementTagId" : elementTagId,
                    "profile" : profile,
                    "form" : form
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'user/profile/profile.html', context)
    
    def post(self, request, id, *args, **kwargs):
        user = get_object_or_404(User, id = id)
        profile = Profile.objects.get(user = user)
        username = user.username

        form = UserProfileForm(request.POST, request.FILES or None, instance = profile)
        
        if form.is_valid():
            user = form.save(commit = False)
            user.username = username
                
            return HttpResponse(status=204)
        
        else:
            return HttpResponse(status=404)
    
class SourceCompanyUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        sourceCompany = SourceCompany.objects.get(id = int(request.GET.get("sc")))
        profile.sourceCompany = sourceCompany
        profile.save()
        
        return redirect("/")
        #return HttpResponse(status=204)
    
class LightThemeUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        request.user.profile.theme = "light"
        request.user.profile.save()
        print(request.user.profile.theme)
        
        return redirect("/")
        #return HttpResponse(status=204)
    
class DarkThemeUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        request.user.profile.theme = "dark"
        request.user.profile.save()
        print(request.user.profile.theme)
        
        return redirect("/")
        #return HttpResponse(status=204)

class CardColorUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Update Card Color")

        color = request.GET.get("color")
            
        profile = request.user.profile
        profile.cardColor = color
        profile.save()
        
        return HttpResponse(status=204)
 

class AccessAuthorizationDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Access Authorizations")
        elementTag = "accessAuthorization"
        elementTagSub = "accessAuthorizationPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'user/access_authorizations.html', context)

class AccessAuthorizationAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Access Authorization")
        elementTag = "accessAuthorization"
        elementTagSub = "accessAuthorizationPart"
        
        pageLoad(request,0,100,"false")
        
        form = AccessAuthorizationForm(request.POST or None, request.FILES or None)
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
        
        return render(request, 'user/access_authorization_add.html', context)
    def post(self, request, *args, **kwargs):
        pageLoad(request,0,100,"false")
        form = AccessAuthorizationForm(request.POST, request.FILES or None)
        
        if form.is_valid():
            accessAuthorization = form.save(commit = False)
            accessAuthorization.user = request.user
            accessAuthorization.sessionKey = request.session.session_key
            
            if not accessAuthorization.name:
                data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":"Name field must be fill!"
                    }
                
                sendAlert(data,"default")
            
            accessAuthorization.save()

            pageLoad(request,100,100,"true")

            return HttpResponse(status=204)
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'user/access_authorization_add.html', context)

class AccessAuthorizationUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Access Authorization Detail")
        elementTag = "accessAuthorization"
        elementTagSub = "accessAuthorizationPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        accessAuthorizations = AccessAuthorization.objects.filter()
        pageLoad(request,20,100,"false")
        accessAuthorization = get_object_or_404(AccessAuthorization, id = id)
        pageLoad(request,40,100,"false")
        pageLoad(request,60,100,"false")
        pageLoad(request,80,100,"false")
        
        # addParts = Part.objects.filter(maker = requestt.maker, type = requestt.makerType)
        # partsLength = len(addParts)
        
        form = AccessAuthorizationForm(request.POST or None, request.FILES or None, instance = accessAuthorization)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "accessAuthorizations" : accessAuthorizations,
                "accessAuthorization" : accessAuthorization,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'user/access_authorization_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        accessAuthorization = get_object_or_404(AccessAuthorization, id = id)
        user = accessAuthorization.user
        sessionKey = accessAuthorization.sessionKey
        pageLoad(request,20,100,"false")
        form = AccessAuthorizationForm(request.POST, request.FILES or None, instance = accessAuthorization)
        if form.is_valid():
            accessAuthorization = form.save(commit = False)
            accessAuthorization.user = user
            accessAuthorization.sessionKey = sessionKey
            
            accessAuthorization.save()
            
            pageLoad(request,100,100,"true")
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)
  

class AccessAuthorizationDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Access Authorization")
        elementTag = "accessAuthorization"
        elementTagSub = "accessAuthorizationPart"
        
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
        
        return render(request, 'user/access_authorization_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            accessAuthorization = get_object_or_404(AccessAuthorization, id = int(id))
            pageLoad(request,90,100,"false")
            accessAuthorization.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
    
class DataAuthorizationDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Data Authorizations")
        elementTag = "dataAuthorization"
        elementTagSub = "dataAuthorizationPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'user/data_authorizations.html', context)

class DataAuthorizationAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Data Authorization")
        elementTag = "dataAuthorization"
        elementTagSub = "dataAuthorizationPart"
        
        pageLoad(request,0,100,"false")
        
        form = DataAuthorizationForm(request.POST or None, request.FILES or None)
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
        
        return render(request, 'user/data_authorization_add.html', context)
    def post(self, request, *args, **kwargs):
        pageLoad(request,0,100,"false")
        form = DataAuthorizationForm(request.POST, request.FILES or None)
        
        if form.is_valid():
            dataAuthorization = form.save(commit = False)
            dataAuthorization.user = request.user
            dataAuthorization.sessionKey = request.session.session_key
            
            if not dataAuthorization.name:
                data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":"Name field must be fill!"
                    }
                
                sendAlert(data,"default")
            
            dataAuthorization.save()

            pageLoad(request,100,100,"true")

            return HttpResponse(status=204)
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'user/data_authorization_add.html', context)

class DataAuthorizationUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Data Authorization Detail")
        elementTag = "dataAuthorization"
        elementTagSub = "dataAuthorizationPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        dataAuthorizations = DataAuthorization.objects.filter()
        pageLoad(request,20,100,"false")
        dataAuthorization = get_object_or_404(DataAuthorization, id = id)
        pageLoad(request,40,100,"false")
        pageLoad(request,60,100,"false")
        pageLoad(request,80,100,"false")
        
        # addParts = Part.objects.filter(maker = requestt.maker, type = requestt.makerType)
        # partsLength = len(addParts)
        
        form = DataAuthorizationForm(request.POST or None, request.FILES or None, instance = dataAuthorization)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "dataAuthorizations" : dataAuthorizations,
                "dataAuthorization" : dataAuthorization,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'user/data_authorization_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        dataAuthorization = get_object_or_404(DataAuthorization, id = id)
        user = dataAuthorization.user
        sessionKey = dataAuthorization.sessionKey
        pageLoad(request,20,100,"false")
        form = DataAuthorizationForm(request.POST, request.FILES or None, instance = dataAuthorization)
        if form.is_valid():
            dataAuthorization = form.save(commit = False)
            dataAuthorization.user = user
            dataAuthorization.sessionKey = sessionKey
            
            dataAuthorization.save()
            
            pageLoad(request,100,100,"true")
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)
  

class DataAuthorizationDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Data Authorization")
        elementTag = "dataAuthorization"
        elementTagSub = "dataAuthorizationPart"
        
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
        
        return render(request, 'user/data_authorization_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            dataAuthorization = get_object_or_404(DataAuthorization, id = int(id))
            pageLoad(request,90,100,"false")
            dataAuthorization.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
    
class UserAuthorizationDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("User Authorizations")
        elementTag = "userAuthorization"
        elementTagSub = "userAuthorizationPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'user/user_authorizations.html', context)
    
class UserAuthorizationUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("User Authorization Detail")
        elementTag = "userAuthorization"
        elementTagSub = "userAuthorizationPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        pageLoad(request,20,100,"false")
        profile = get_object_or_404(Profile, user = id)
        pageLoad(request,40,100,"false")
        accessAuthorizations = AccessAuth.objects.filter().order_by("name")
        dataAuthorizations = DataAuth.objects.filter().order_by("name")
        profileAccessAuthorizations = profile.accessAuth.all()
        profileDataAuthorizations = profile.dataAuth.all()
        pageLoad(request,60,100,"false")
        pageLoad(request,80,100,"false")
        
        form = UserAuthorizationForm(request.POST or None, request.FILES or None, instance = profile)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "profile" : profile,
                "accessAuthorizations" : accessAuthorizations,
                "dataAuthorizations" : dataAuthorizations,
                "profileAccessAuthorizations"  :profileAccessAuthorizations,
                "profileDataAuthorizations"  :profileDataAuthorizations,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'user/user_authorization_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        profile = get_object_or_404(Profile, user = id)
        pageLoad(request,20,100,"false")
        
        keyList = list(request.POST.keys())
        keyList.remove("csrfmiddlewaretoken")
        
        accessAuthorizationList = []
        dataAuthorizationList = []
        
        for item in keyList:
            if item.startswith("accessAuthorization"):
                accessAuthorizationList.append(item.split('-')[1])
            elif item.startswith("dataAuthorization"):
                dataAuthorizationList.append(item.split('-')[1])
        
        profile.accessAuth.clear()
        profile.dataAuth.clear()
        
        for item in accessAuthorizationList:
            accessAuthorization = AccessAuth.objects.filter(code = item).first()
            profile.accessAuth.add(accessAuthorization)
            
        for item in dataAuthorizationList:
            dataAuthorization = DataAuth.objects.filter(code = item).first()
            profile.dataAuth.add(dataAuthorization)
            
        profile.save()
        
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)

class MaintenanceView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            
            }
        
        return render(request, 'user/user_profile.html', context)