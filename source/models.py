import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
# Create your models here.
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model

from ckeditor.fields import RichTextField

from card.models import Country, City, Currency

def company_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.id is None:
        return 'source/companies/temp/{0}/{1}'.format(instance.id, filename)
    else:
        return 'source/companies/{0}/{1}'.format(instance.id, filename)

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="unknown")[0]

class Company(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="administration_access_authorization_user")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    name = models.CharField(_("Company Name"), max_length=140)
    formalName = models.CharField(_("Company Formal Name"), max_length=140, blank = True, null=True)
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "SC", blank = True, null=True)
    code = models.CharField(_("Company Code"), max_length=140, blank = True, null = True)
    companyNo = models.CharField(_("Company No"), max_length=140, blank = True, null=True)
    
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name = "source_company_country", blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.DO_NOTHING, related_name = "source_company_city",)
    address = models.TextField(_("Address"), blank=True, null=True)
    
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
    
    logo = models.ImageField(_("Logo"), blank = True, null = True, upload_to = company_directory_path)
    documentLogo = models.ImageField(_("Document Logo"), blank = True, null = True, upload_to = company_directory_path)
    
    about = models.TextField(_("About"), blank = True, null = True)
    
    saleRequestCode = models.CharField(_("Sale Request Code"), max_length=50, default = "", blank = True, null=True)
    saleInquiryCode = models.CharField(_("Sale Inquiry Code"), max_length=50, default = "", blank = True, null=True)
    saleQuotationCode = models.CharField(_("Sale Quotation Code"), max_length=50, default = "", blank = True, null=True)
    saleOrderConfirmationCode = models.CharField(_("Sale Order Confirmation Code"), max_length=50, default = "", blank = True, null=True)
    saleOrderNotConfirmationCode = models.CharField(_("Sale Order Not Confirmation Code"), max_length=50, default = "", blank = True, null=True)
    salePurchaseOrderCode = models.CharField(_("Sale Purchase Order Code"), max_length=50, default = "", blank = True, null=True)
    saleDispatchOrderCode = models.CharField(_("Sale Dispatch Order Code"), max_length=50, default = "", blank = True, null=True)
    serviceAcceptaneCode = models.CharField(_("Service Acceptane Code"), max_length=50, default = "", blank = True, null=True)
    serviceOfferCode = models.CharField(_("Service Offer Code"), max_length=50, default = "", blank = True, null=True)
    purchasingProjectCode = models.CharField(_("Purchasing Project Code"), max_length=50, default = "", blank = True, null=True)
    purchasingInquiryCode = models.CharField(_("Purchasing Inquiry Code"), max_length=50, default = "", blank = True, null=True)
    purchasingPurchaseOrderCode = models.CharField(_("Purchasing Purchase Order Code"), max_length=50, default = "", blank = True, null=True)
    accountIncomingInvoiceCode = models.CharField(_("Account Incoming Invoice Code"), max_length=50, default = "", blank = True, null=True)
    accountSendInvoiceCode = models.CharField(_("Account Send Invoice Code"), max_length=50, default = "", blank = True, null=True)
    accountProformaInvoiceCode = models.CharField(_("Account Proforma Invoice Code"), max_length=50, default = "", blank = True, null=True)
    accountCommercialInvoiceCode = models.CharField(_("Account Commercial Invoice Code"), max_length=50, default = "", blank = True, null=True)
    accountPaymentCode = models.CharField(_("Account Payment Code"), max_length=50, default = "", blank = True, null=True)

    sendInvoicePdfHtml = RichTextField(_("Send Invoice Pdf Html"), max_length=30000, blank = True, null = True, config_name='default')
    
    mikroDBName = models.CharField(_("Mikro DB Name"), max_length=150, default = "", blank = True, null=True)
    
    def save(self, *args, **kwargs):
        if self.id is None:
            savedLogo = self.logo
            self.logo = None
            super(Company, self).save(*args, **kwargs)
            self.logo = savedLogo
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        if self.formalName is None:
            self.formalName = self.name
        super(Company, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']
        
class Bank(models.Model):
    """
    Stores the currency info
    """
    user = models.ForeignKey("auth.User", on_delete=models.DO_NOTHING, related_name = "source_bank_user", blank = True)
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
    currency = models.ForeignKey(Currency, related_name = "source_bank_currency", on_delete=models.SET_NULL, blank=True, null=True)
    
    balance = models.FloatField(_("Balance"), default = 0, blank = True, null = True)
    
    history = HistoricalRecords()

    def __str__(self):
        return str(self.bankName)

    class Meta:
        ordering = ['bankName']
        
