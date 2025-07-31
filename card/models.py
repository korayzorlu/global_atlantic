import os

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
# Create your models here.
from simple_history.models import HistoricalRecords

from ckeditor.fields import RichTextField
from django.utils import timezone

from simple_history.models import HistoricalRecords

from user.models import Profile

import account

def company_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.id is None:
        return 'companies/temp/{0}/{1}'.format(instance.id, filename)
    else:
        return 'companies/{0}/{1}'.format(instance.id, filename)

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="unknown")[0]

class Country(models.Model):
    """
    Stores the country info
    """
    formal_name = models.CharField(_("Country Name"), max_length=140)
    international_formal_name = models.CharField(_("International Formal Country Name"), max_length=140)
    iso2 = models.CharField(_("ISO2"), max_length=100, null=True, blank=True)
    iso3 = models.CharField(_("ISO3"), max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.formal_name

    class Meta:
        ordering = ['formal_name']


class City(models.Model):
    """
    Stores the city info
    """
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True, related_name="cities")
    name = models.CharField(_("City"), max_length=100, null=True, blank=True)
    capital = models.BooleanField(_("Capital"), default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']
        
class Currency(models.Model):
    """
    Stores the currency info
    """
    country = models.CharField(_("Country"), max_length=140)
    currency = models.CharField(_("Currency"), max_length=140)
    code = models.CharField(_("Code"), max_length=140)
    symbol = models.CharField(_("Symbol"), max_length=140)
    flag = models.CharField(_("Flag"), max_length=140)
    
    BASE_CURRENCIES = (
        ('try', _('TRY')),
        ('usd', _('USD')),
    )
    baseCurrency = models.CharField(_("Base Currency"), max_length=40, default="try", choices = BASE_CURRENCIES)
    forexBuying = models.FloatField(_("Forex Buying"), default = 0.00, null = True, blank = True)
    forexSelling = models.FloatField(_("Forex Selling"), default = 0.00, null = True, blank = True)
    banknoteBuying = models.FloatField(_("Banknote Buying"), default = 0.00, null = True, blank = True)
    banknoteSelling = models.FloatField(_("Banknote Selling"), default = 0.00, null = True, blank = True)
    rateUSD = models.FloatField(_("Rate USD"), null = True, blank = True)
    rateOther = models.FloatField(_("Rate Other"), null = True, blank = True)
    rateDate = models.DateField(_("Rate Date"), default = timezone.now, blank = True)
    tcmbRateDate = models.CharField(_("TCMB Rate Date"), max_length=40, null=True, blank=True)

    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.currency)

    class Meta:
        ordering = ['currency']

class Company(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="company_source_company")
    role = models.JSONField(_("Role"),blank=True, null=True)
    customerCheck = models.BooleanField(_("Customer"), default = False)
    supplierCheck = models.BooleanField(_("Supplier"), default = False)
    agentCheck = models.BooleanField(_("Agent"), default = False)
    ourCompany = models.BooleanField(_("Our Company"), default = False)
    
    name = models.CharField(_("Company Name"), max_length=140)
    lowerName = models.CharField(_("Lower Company Name"), default = "", max_length=140, blank=True, null=True)
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "C", blank = True, null=True)
    code = models.CharField(_("Company Code"), max_length=140, blank = True, null = True)
    companyNo = models.CharField(_("Company No"), max_length=140, blank = True, null=True)
    
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.DO_NOTHING)
    address = models.CharField(_("Address"), max_length=150, blank=True, null=True)
    addressChar = models.CharField(_("Address Char"), max_length=150, blank=True, null=True)
    
    vatOffice = models.CharField(_("Vat Office"), max_length=100, blank=True, null=True)
    vatNo = models.CharField(_("Vat No"), max_length=50, blank=True, null=True)
    
    phone1 = models.CharField(_("Phone 1"), max_length=50, blank=True, null=True)
    phone2 = models.CharField(_("Phone 2"), max_length=50, blank=True, null=True)
    phone3 = models.CharField(_("Phone 2"), max_length=50, blank=True, null=True)
    phone4 = models.CharField(_("Phone 2"), max_length=50, blank=True, null=True)
    phone5 = models.CharField(_("Phone 2"), max_length=50, blank=True, null=True)
    
    fax = models.CharField(_("Fax 1"), max_length=50, blank=True, null=True)
    
    email = models.EmailField(_("Email"), blank=True, null=True)
    web = models.URLField(max_length=100, blank=True, null=True)
    
    hesapKodu = models.CharField(_("Hesap Kodu"), max_length=50, blank=True, null=True)
    satisTemsilcisi = models.ForeignKey(Profile, related_name = "satis_temsilcisi", on_delete=models.DO_NOTHING, blank=True, null=True)
    
    creditPeriot = models.CharField(_("Credit Periot"), max_length=50, blank=True, null=True)
    creditPeriod = models.IntegerField(_("Credit Period"), default=30, blank = True, null = True)
    
    logo = models.ImageField(_("Logo"), blank = True, null = True, upload_to = company_directory_path)
    
    creditLimit = models.FloatField(_("Credit Limit"), default = 0.00, blank=True, null=True)
    credit = models.FloatField(_("Credit"), default = 0.00, blank=True, null=True)
    currency = models.ForeignKey(Currency, related_name = "curency", on_delete=models.SET_NULL, blank=True, null=True)
    unlimitedCheck = models.BooleanField(_("Unlimited"), default = False)
    
    currency2 = models.ForeignKey(Currency, related_name = "curency_2", on_delete=models.SET_NULL, blank=True, null=True)
    currency3 = models.ForeignKey(Currency, related_name = "curency_3", on_delete=models.SET_NULL, blank=True, null=True)
    
    overPaid = models.JSONField(_("Over Paid"), blank = True, null = True)
    
    mikroGuid = models.CharField(_("Mikro Guid"), max_length=150, blank=True, null=True)
    eFatura = models.BooleanField(_("E-Fatura"), default = False)
    
    debt = models.FloatField(_("Debt"), default = 0.00, blank = True)
    
    about = models.TextField(_("About"), blank = True, null = True)
    
    def save(self, *args, **kwargs):
        if self.id is None:
            savedLogo = self.logo
            self.logo = None
            super(Company, self).save(*args, **kwargs)
            self.logo = savedLogo
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        self.role = {"customer" : self.customerCheck, "supplier" : self.supplierCheck, "agent" : self.agentCheck, "ourCompany" : self.ourCompany}
        
        
        
        
        
        super(Company, self).save(*args, **kwargs)

    def get_fields(self):
        ignore = ('id', 'created_at', 'updated_at')
        result = []
        for field in self._meta.fields:
            if field.name not in ignore:
                if self._meta.get_field(field.name).__class__.__name__ == "BooleanField":
                    value = True if getattr(self, field.name) else "False"
                elif field.choices:
                    value = getattr(self, f"get_{field.name}_display")()
                else:
                    value = getattr(self, field.name)
                result.append((field.verbose_name.title(), value if value else ''))
        return result

    def available_vessels(self):
        return self.vessels.filter(status="available")
    
    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

class Current(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="current_source_company")
    company = models.ForeignKey(Company, related_name = "current_company", on_delete=models.DO_NOTHING)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "current_currency", default = 106, blank = True, null = True)
    debt = models.FloatField(_("Debt"), default = 0.00, blank = True)
    credit = models.FloatField(_("Credit"), default = 0.00, blank = True)
    #processJSON = models.JSONField(_("Process"), blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.company.name)

    class Meta:
        ordering = ['company']

class Vessel(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="vessel_source_company")
    name = models.CharField(_("Vessel Name"), max_length=140)
    company = models.ForeignKey(Company, related_name = "company", on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(Company, related_name = "owner", on_delete=models.DO_NOTHING, blank = True, null = True)
    
    flag = models.CharField(_("Flag"), max_length=140, blank = True, null = True)
    shipyard = models.CharField(_("Shipyard"), max_length=140, blank = True, null = True)
    hallNo = models.CharField(_("Hall No"), max_length=140, blank = True, null = True)
    imo = models.CharField(_("IMO"), max_length=140)
    mmsi = models.CharField(_("MMSI"), max_length=140, blank = True, null = True)
    callSign = models.CharField(_("Call Sign"), max_length=140, blank = True, null = True)
    
    TYPES = (
        ('aht', _('AHT')),('ahts', _('AHTS')),('aor', _('AOR')),('atb', _('ATB')),('c/f', _('C/F')),('crv', _('CRV')),('cs', _('CS')),('db', _('DB')),
        ('dcv', _('DCV')),('depv', _('DEPV')),('dlb', _('DLB')),('dsv', _('DSV')),('dv', _('DV')),('errv', _('ERRV')),('fpso', _('FPSO')),('fpv', _('FPV')),
        ('ft', _('FT')),('fv', _('FV')),('gts', _('GTS')),('hlv', _('HLV')),('hsc', _('HSC')),('hsf', _('HSF')),('htv', _('HTV')),('irv', _('IRV')),
        ('itb', _('ITB')),('lb', _('LB')),('lng/c', _('LNG/C')),('lpg/c', _('LPG/C')),('m/f', _('M/F')),('m/s', _('M/S')),('m/t', _('M/T')),('m/tug', _('M/TUG')),
        ('m/v', _('M/V')),('m/y', _('M/Y')),('msv', _('MSV')),('msy', _('MSY')),('mts', _('MTS')),('my', _('MY')),('nb', _('NB')),('nrv', _('NRV')),
        ('ns', _('NS')),('osv', _('OSV')),('pp', _('PP')),('ps', _('PS')),('psv', _('PSV')),('qsmv', _('QSMV')),('qtev', _('QTEV')),('rms', _('RMS')),
        ('rnlb', _('RNLB')),('rsv', _('RSV')),('sb', _('SB')),('ss', _('SS')),('sscv', _('SSCV')),('sss', _('SSS')),('ssv', _('SSV')),('st', _('ST')),
        ('sts', _('STS')),('stv', _('STV')),('sv', _('SV')),('sy', _('SY')),('tev', _('TEV')),('tiv', _('TIV')),('ts', _('TS')),('tss', _('TSS')),('tv', _('TV')),
    )
    
    type = models.CharField(_("Type"), max_length=40, default="day", choices = TYPES)
    
    building = models.CharField(_("Building"), max_length=140, blank = True, null = True)
    grosston = models.CharField(_("Grosston"), max_length=140, blank = True, null = True)
    deadWeight = models.CharField(_("Dead Weight"), max_length=140, blank = True, null = True)
    loa = models.CharField(_("LOA"), max_length=140, blank = True, null = True)
    beam = models.CharField(_("Beam"), max_length=140, blank = True, null = True)
    draft = models.CharField(_("Draft"), max_length=140, blank = True, null = True)
    draught = models.CharField(_("Draught"), max_length=140, blank = True, null = True)
    classificationSociety = models.CharField(_("Classification Society"), max_length=140, blank = True, null = True)
    
    parts = models.JSONField(_("Parts"),blank=True, null=True)
    
    history = HistoricalRecords()
    
    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

class Owner(models.Model):
    """
    Stores the currency info
    """
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="owner_source_company")
    ownerCompany = models.ForeignKey(Company, related_name = "owner_company", on_delete=models.DO_NOTHING)
    user = models.ForeignKey("auth.User", on_delete=models.DO_NOTHING)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    name = models.CharField(_("Owner Name"), max_length=140, blank = True, null = True)
    vessel = models.ForeignKey(Vessel, on_delete=models.SET_NULL, blank = True, null = True, related_name = "owner_vessel")

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']
        
class Billing(models.Model):
    """
    Stores the currency info
    """
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="billing_source_company")
    name = models.CharField(_("Billing Name"), max_length=140, blank = True, null = True)
    address = models.TextField(_("Address"), max_length=500,blank=True, null=True)
    user = models.ForeignKey("auth.User", blank=True, null=True,on_delete=models.DO_NOTHING)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    vessel = models.ForeignKey(Vessel, on_delete=models.SET_NULL, blank = True, null = True, related_name = "billing_vessel")
    
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.DO_NOTHING)
    address = models.CharField(_("Address"), max_length = 150, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    
    vatOffice = models.CharField(_("Vat Office"), max_length=100, blank=True, null=True)
    vatNo = models.CharField(_("Vat No"), max_length=50, blank=True, null=True)
    
    hesapKodu = models.CharField(_("Hesap Kodu"), max_length=50, blank=True, null=True)
    mikroGuid = models.CharField(_("Mikro Guid"), max_length=150, blank=True, null=True)
    currency = models.ForeignKey(Currency, related_name = "billing_curency", on_delete=models.SET_NULL, blank=True, null=True)
    currency2 = models.ForeignKey(Currency, related_name = "billing_curency_2", on_delete=models.SET_NULL, blank=True, null=True)
    currency3 = models.ForeignKey(Currency, related_name = "billing_curency_3", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

class EnginePart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="engine_part_ssource_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, blank = True, null = True)
    
    maker = models.ForeignKey("data.Maker", on_delete=models.CASCADE, related_name = "engine_part_maker")
    makerType = models.ForeignKey("data.MakerType", on_delete=models.CASCADE, related_name = "engine_part_type")
    category = models.CharField(_("Category"), max_length=140, blank = True, null = True)
    serialNo = models.CharField(_("Serial No"), max_length=140, blank = True, null = True)
    cyl = models.CharField(_("Cyl"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), blank = True, null = True)
    version = models.CharField(_("Version"), max_length=140, blank = True, null = True)
    
    def __str__(self):
        return str(self.serialNo)

    class Meta:
        ordering = ['serialNo']

class Person(models.Model):
    """
    Stores the currency info
    """
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="person_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.DO_NOTHING)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    name = models.CharField(_("Personal Name"), max_length=140, blank = True, null = True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank = True, null = True)
    vessel = models.ForeignKey(Vessel, on_delete=models.SET_NULL, blank = True, null = True)
    title = models.CharField(_("Title"), max_length=140, blank = True, null = True)
    email = models.EmailField(_("Email"), blank = True, null = True)
    phone = models.CharField(_("Phone 1"), max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']
        
class Bank(models.Model):
    """
    Stores the currency info
    """
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="bank_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.DO_NOTHING)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank = True, null = True)
    
    BANK_ACCOUNTS = (
        ('vadesiz', _('Vadesiz')),
        ('mevduat', _('Mevduat')),
    )
    
    bankName = models.CharField(_("Bank name"), max_length=200, blank = True, null = True)
    accountNo = models.CharField(_("Account No"), max_length=50, blank=True, null=True)
    ibanNo = models.CharField(_("IBAN"), max_length=50, blank=True, null=True)
    accountType = models.CharField(_("Type"), max_length=40, default="vadesiz", choices = BANK_ACCOUNTS)
    swiftNo = models.CharField(_("Swift No"), max_length=50, blank=True, null=True)
    branchName = models.CharField(_("Branch Name"), max_length=50, blank=True, null=True)
    branchCode = models.CharField(_("Branch Code"), max_length=50, blank=True, null=True)
    currency = models.ForeignKey(Currency, related_name = "bank_currency", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.bankName)

    class Meta:
        ordering = ['bankName']



class Excel(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="card_excel_source_company")
    file = models.FileField(blank =True, null = True, verbose_name = "Excel File")
    

        