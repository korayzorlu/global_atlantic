import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
# Create your models here.
from simple_history.models import HistoricalRecords

from ckeditor.fields import RichTextField
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model

from django_filters import FilterSet, ChoiceFilter

from card.models import Currency, Company, Vessel, Billing
from sale.models import Project, Request, PurchaseOrder, PurchaseOrderPart, OrderConfirmation, QuotationPart, OrderTracking,QuotationExtra
from source.models import Bank as SourceBank
from source.models import Company as SourceCompany
from service.models import Offer, OfferServiceCard, OfferExpense, OfferPart
from data.models import Expense, Part, ServiceCard
from purchasing.models import Project as PurchasingProject
from purchasing.models import PurchaseOrder as PurchasingPurchaseOrder
from purchasing.models import PurchaseOrderItem as PurchasingPurchaseOrderItem

from datetime import datetime, timedelta


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="unknown")[0]

class IncomingInvoice(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="incoming_invoice_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name="incoming_invoice", blank = True, null = True, )
    purchasingProject = models.ForeignKey(PurchasingProject, on_delete=models.SET_NULL, related_name="purchasing_incoming_invoice", blank = True, null = True, )
    theRequest = models.ForeignKey(Request, on_delete=models.SET_NULL, blank = True, null = True, related_name="incoming_invoice_request")
    purchaseOrder = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, blank = True, null = True, related_name="incoming_invoice_purchase_order")
    purchasingPurchaseOrder = models.ForeignKey(PurchasingPurchaseOrder, on_delete=models.SET_NULL, blank = True, null = True, related_name="purchasing_incoming_invoice_purchase_order")

    seller = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="incoming_invoice_seller", blank = True, null = True)
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="incoming_invoice_customer", blank = True, null = True)
    customerSource = models.ForeignKey(SourceCompany, on_delete=models.DO_NOTHING, related_name="incoming_invoice_customer_source", blank = True, null = True)
    
    GROUPS = (
        ('order', _('Order')),
        ('service', _('Service')),
        ('purchasing', _('Purchasing')),
    )
    
    group = models.CharField(max_length=30, choices=GROUPS, default = "order", blank=True, null=True)
    
    awb = models.CharField(_("AWB"), max_length=140, blank = True, null=True)
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    
    incomingInvoiceNo = models.CharField(_("Incoming Invoice No"), max_length=140, blank = True, null=True)
    
    incomingInvoiceDate = models.DateField(_("Incoming Invoice Date"), default = timezone.now, blank = True)
    
    paymentDate = models.DateField(_("Payment Date"), default = timezone.now, blank = True)

    deliveryDate = models.DateField(_("Delivery Date"), null = True, blank = True)
    deliveryNo = models.CharField(_("Delivery No"), max_length=140, blank = True, null=True)
    deliveryNote = models.CharField(_("Delivery Note"), max_length=250, blank = True, null = True)
    
    transport = models.CharField(_("Transport"), max_length=250, blank = True, null = True)
    
    ready = models.BooleanField(_("Ready"), default = False)
    payed = models.BooleanField(_("Payed"), default = False)
    
    discountPrice = models.FloatField(_("Discount Price"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    netPrice = models.FloatField(_("Net Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    paidPrice = models.FloatField(_("Paid Price"), default = 0, blank = True, null = True)
    
    exchangeRate = models.FloatField(_("Exchange Rate"), default = 0, blank = True, null = True)
    
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "incoming_invoice_currency", default = 106, blank = True, null = True)
    
    #parts = models.ManyToManyField(PurchaseOrderPart,related_name='incoming_invoices',through='IncomingInvoicePart', blank = True, null=True)

    #timestamp = models.TimeField(auto_now_add=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.incomingInvoiceNo)

    class Meta:
        ordering = ['incomingInvoiceDate']

class IncomingInvoicePart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="incoming_invoice_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(IncomingInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    purchaseOrderPart = models.ForeignKey(PurchaseOrderPart, on_delete=models.CASCADE, related_name = "incoming_invoice_part_part", blank = True, null = True)
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "incoming_invoice_part_manuel_part", blank = True, null = True)
    
    UNITS = (
        ('day', _('Day')),
        ('hrs', _('HRS')),
        ('kg', _('Kg')),
        ('m²', _('m²')),
        ('mm', _('MM')),
        ('pc', _('Pc')),
        ('pcs', _('PCS')),
        ('pk', _('PK')),
        ('persons', _('Persons')),
    )
    
    partNo = models.CharField(_("Part No"), max_length=140, null=True, blank = True)
    unit = models.CharField(_("Units"), default = "pc", max_length=40, choices = UNITS)
    description = models.TextField(_("Description"), max_length=250, blank = True)
    
    quantity = models.FloatField(default=1)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)

    placed = models.BooleanField(_("Placed"), default = False)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * float(self.quantity)
        
        super(IncomingInvoicePart, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.part.partNo)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['purchaseOrderPart', 'invoice'], name='unique_purchaseOrderPart_invoice')
        ]
        
class IncomingInvoiceItem(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="incoming_invoice_item_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(IncomingInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    trDescription = models.TextField(_("Turkish Description"), max_length=250, null=True, blank = True)
    
    purchaseOrderPart = models.ForeignKey(PurchaseOrderPart, on_delete=models.DO_NOTHING, related_name = "incoming_invoice_purchase_order_part", blank = True, null = True)
    purchasingPurchaseOrderItem = models.ForeignKey(PurchasingPurchaseOrderItem, on_delete=models.DO_NOTHING, related_name = "purchasing_incoming_invoice_purchase_order_item", blank = True, null = True)

    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "incoming_invoice_part", blank = True, null = True)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name = "incoming_invoice_expense", blank = True, null = True)
    
    name = models.CharField(_("Item Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    UNITS = (
        ('day', _('Day')),
        ('hrs', _('HRS')),
        ('kg', _('Kg')),
        ('m²', _('m²')),
        ('mm', _('MM')),
        ('pc', _('Pc')),
        ('pcs', _('PCS')),
        ('pk', _('PK')),
        ('persons', _('Persons')),
    )
    unit = models.CharField(_("Units"), max_length=40, default = "pc", choices = UNITS)
    
    quantity = models.FloatField(default=1)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)

    placedItems = models.FloatField(_("Placed Items"), default = 0, blank = True, null = True)
    placed = models.BooleanField(_("Placed"), default = False)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(IncomingInvoiceItem, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)

# class IncomingInvoiceManuelPart(models.Model):
#     user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
#     sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
#     invoice = models.ForeignKey(IncomingInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
#     part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "incoming_invoice_part_part", blank = True)
#     quantity = models.FloatField(default=1)
    
#     sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
#     unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
#     totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
#     vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
#     vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    
#     def save(self, *args, **kwargs):
        
#         #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
#         super(IncomingInvoiceManuelPart, self).save(*args, **kwargs)
    
#     def __str__(self):
#         return str(self.part.partNo)

class IncomingInvoiceExpense(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="incoming_invoice_expense_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(IncomingInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, blank = True, null = True)
    
    UNITS = (
        ('day', _('Day')),
        ('hrs', _('HRS')),
        ('kg', _('Kg')),
        ('m²', _('m²')),
        ('mm', _('MM')),
        ('pc', _('Pc')),
        ('pcs', _('PCS')),
        ('pk', _('PK')),
        ('persons', _('Persons')),
    )
    
    unit = models.CharField(_("Units"), default = "pc", max_length=40, choices = UNITS)
    
    name = models.CharField(_("Billing Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500,blank=True, null=True)
    
    quantity = models.FloatField(default=1)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name'] 
       
class SendInvoice(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="send_invoice_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name="send_invoice", blank = True, null = True, )
    theRequest = models.ForeignKey(Request, on_delete=models.SET_NULL, blank = True, null = True, related_name="send_invoice_request")
    orderConfirmation = models.ForeignKey(OrderConfirmation, on_delete=models.SET_NULL, blank = True, null = True, related_name="send_invoice_order_confirmation")
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, blank = True, null = True, related_name="send_invoice_offer")
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Send Invoice Year"), max_length=140, blank = True, null = True)
    code = models.IntegerField(_("Send Invoice Code"), blank = True, null = True)
    sendInvoiceNoSys = models.CharField(_("Send Invoice No"), max_length=140, blank = True, null=True)
    
    seller = models.ForeignKey(SourceCompany, on_delete=models.DO_NOTHING, related_name="send_invoice_seller", blank = True, null = True)
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="send_invoice_customer", blank = True, null = True)
    vessel = models.ForeignKey(Vessel, on_delete=models.DO_NOTHING, related_name="send_invoice_vessel", blank = True, null = True)
    billing = models.ForeignKey(Billing, on_delete=models.DO_NOTHING, related_name="send_invoice_billing", blank = True, null = True)
    
    GROUPS = (
        ('order', _('Order')),
        ('service', _('Service')),
    )
    
    group = models.CharField(max_length=30, choices=GROUPS, default = "order", blank=True, null=True)
    
    awb = models.CharField(_("AWB"), max_length=140, blank = True, null=True)
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    
    sendInvoiceNo = models.CharField(_("Send Invoice No"), max_length=140, unique = True, blank = True, null=True)
    
    sendInvoiceDate = models.DateField(_("Send Invoice Date"), default = timezone.now, blank = True)
    
    paymentDate = models.DateField(_("Payment Date"), default = timezone.now, blank = True)

    deliveryDate = models.DateField(_("Delivery Date"), null = True, blank = True)
    deliveryNo = models.CharField(_("Delivery No"), max_length=140, blank = True, null=True)
    
    careOf = models.CharField(_("Care Of"), max_length=250, blank = True, null = True)
    transport = models.CharField(_("Transport"), max_length=250, blank = True, null = True)
    
    ready = models.BooleanField(_("Ready"), default = False)
    payed = models.BooleanField(_("Payed"), default = False)
    
    extraDiscountPrice = models.FloatField(_("Extra Discount Price"), default = 0, blank = True, null = True)
    discountPrice = models.FloatField(_("Discount Price"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    netPrice = models.FloatField(_("Net Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    paidPrice = models.FloatField(_("Paid Price"), default = 0, blank = True, null = True)
    exchangeRate = models.FloatField(_("Exchange Rate"), default = 0, blank = True, null = True)
    only = models.CharField(_("Onyl"), max_length=500, blank = True, null = True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "send_invoice_currency", default = 106, blank = True, null = True)
    
    #parts = models.ManyToManyField(QuotationPart,related_name='send_invoices',through='SendInvoicePart', blank = True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.sendInvoiceNo)


class SendInvoiceItem(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="send_invoice_item_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(SendInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    trDescription = models.TextField(_("Turkish Description"), max_length=250, null=True, blank = True)
    
    quotationPart = models.ForeignKey(QuotationPart, on_delete=models.DO_NOTHING, related_name = "send_invoice_quotation_part", blank = True, null = True)
    quotationExpense = models.ForeignKey(QuotationExtra, on_delete=models.DO_NOTHING, related_name = "send_invoice_quotation_expense", blank = True, null = True)
    offerServiceCard = models.ForeignKey(OfferServiceCard, on_delete=models.DO_NOTHING, related_name = "send_invoice_offer_service_card", blank = True, null = True)
    offerPart = models.ForeignKey(OfferPart, on_delete=models.DO_NOTHING, related_name = "send_invoice_offer_part", blank = True, null = True)
    offerExpense = models.ForeignKey(OfferExpense, on_delete=models.DO_NOTHING, related_name = "send_invoice_offer_expense", blank = True, null = True)
    
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "send_invoice_part", blank = True, null = True)
    serviceCard = models.ForeignKey(ServiceCard, on_delete=models.CASCADE, related_name = "send_invoice_service_card", blank = True, null = True)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name = "send_invoice_expense", blank = True, null = True)
    
    name = models.CharField(_("Expense Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    UNITS = (
        ('day', _('Day')),
        ('hrs', _('HRS')),
        ('kg', _('Kg')),
        ('m²', _('m²')),
        ('mm', _('MM')),
        ('pc', _('Pc')),
        ('pcs', _('PCS')),
        ('pk', _('PK')),
        ('persons', _('Persons')),
    )
    unit = models.CharField(_("Units"), max_length=40, default = "pc", choices = UNITS)
    
    quantity = models.FloatField(default=1)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), max_length=1000, blank = True, null = True)
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(SendInvoiceItem, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)

class SendInvoiceExpense(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="send_invoice_expense_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(SendInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, blank = True, null = True)
    
    UNITS = (
        ('day', _('Day')),
        ('hrs', _('HRS')),
        ('kg', _('Kg')),
        ('m²', _('m²')),
        ('mm', _('MM')),
        ('pc', _('Pc')),
        ('pcs', _('PCS')),
        ('pk', _('PK')),
        ('persons', _('Persons')),
    )
    
    unit = models.CharField(_("Units"), default = "pc", max_length=40, choices = UNITS)
    
    name = models.CharField(_("Billing Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500,blank=True, null=True)
    
    quantity = models.FloatField(default=1)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']
    
class SendInvoicePart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="send_invoice_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(SendInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    trDescription = models.TextField(_("Turkish Description"), max_length=250, null=True, blank = True)
    
    quotationPart = models.ForeignKey(QuotationPart, on_delete=models.CASCADE, related_name = "send_invoice_part_part", blank = True)
    quantity = models.FloatField(default=1)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(SendInvoicePart, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.quotationPart.inquiryPart.requestPart.part.partNo)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['quotationPart', 'invoice'], name='unique_quotationPart_invoice')
        ]
        
class SendInvoiceServiceCard(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="send_invoice_service_car_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(SendInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    trDescription = models.TextField(_("Turkish Description"), max_length=250, null=True, blank = True)
    
    offerServiceCard = models.ForeignKey(OfferServiceCard, on_delete=models.CASCADE, related_name = "send_invoice_partt_part", blank = True)
    quantity = models.FloatField(default=1)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(SendInvoiceServiceCard, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.offerServiceCard.serviceCard.code)
        
class Payment(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="payment_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="payment_customer", blank = True, null = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Payment Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Payment Code"), max_length=140, blank = True, null = True)
    paymentNo = models.CharField(_("Payment No"), max_length=140, blank = True, null=True)
    
    PAYMENT_TYPES = (
        ('in', _('In')),
        ('out', _('Out')),
    )
    
    type = models.CharField(max_length=30, choices=PAYMENT_TYPES, default = "in", blank = True)
    
    paymentDate = models.DateField(_("Payment Date"), default = timezone.now, blank = True)
    
    sourceBank = models.ForeignKey(SourceBank, on_delete=models.SET_NULL, related_name = "payment_source_bank", blank = True, null = True)
    
    invoices = models.JSONField(_("Payment Invoices"), blank = True, null = True)
    
    amount = models.FloatField(_("Amount"), default = 0, blank = True, null = True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "payment_currency", default = 106, blank = True, null = True)

    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.paymentNo)

class PaymentInvoice(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="payment_invoice_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank = True, null = True)

    sendInvoice = models.ForeignKey(SendInvoice, on_delete=models.CASCADE, related_name = "payment_invoice_send_invoice", blank = True, null = True)
    incomingInvoice = models.ForeignKey(IncomingInvoice, on_delete=models.CASCADE, related_name = "payment_invoice_incoming_invoice", blank = True, null = True)
    
    invoicePaymentDate = models.DateField(_("Invoice Payment Date"), default = timezone.now, blank = True)

    TYPES = (
        ('send_invoice', _('Send Invoice')),
        ('incoming_invoice', _('Incoming Invoice')),
    )
    
    type = models.CharField(max_length=30, choices=TYPES, default = "send_invoice", blank=True, null=True)
    
    invoiceCurrencyAmount = models.FloatField(_("Invoice Currency Amount"), default = 0, blank = True, null = True)
    amount = models.FloatField(_("Amount"), default = 0, blank = True, null = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.payment.paymentNo)



class ServiceSendInvoice(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="service_send_invoce_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, blank = True, null = True, related_name="send_invoice_request")
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Service Send Invoice Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Service Send Invoice Code"), max_length=140, blank = True, null = True)
    sendInvoiceNoSys = models.CharField(_("Service Send Invoice No"), max_length=140, blank = True, null=True)

    seller = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="service_send_invoice_seller", blank = True, null = True)
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="service_send_invoice_customer", blank = True, null = True)
    
    GROUPS = (
        ('order', _('Order')),
        ('service', _('Service')),
    )
    
    group = models.CharField(max_length=30, choices=GROUPS, default = "service", blank=True, null=True)
    
    awb = models.CharField(_("AWB"), max_length=140, blank = True, null=True)
    
    sendInvoiceNo = models.CharField(_("Send Invoice No"), max_length=140, blank = True, null=True)
    
    sendInvoiceDate = models.DateField(_("Send Invoice Date"), default = timezone.now, blank = True)
    
    paymentDate = models.DateField(_("Payment Date"), default = timezone.now, blank = True)

    deliveryDate = models.DateField(_("Delivery Date"), null = True, blank = True)
    deliveryNo = models.CharField(_("Delivery No"), max_length=140, blank = True, null=True)
    
    careOf = models.CharField(_("Care Of"), max_length=250, blank = True, null = True)
    transport = models.CharField(_("Transport"), max_length=250, blank = True, null = True)
    
    ready = models.BooleanField(_("Ready"), default = False)
    payed = models.BooleanField(_("Payed"), default = False)
    addToInvoiceExpense = models.BooleanField(_("Add To Invoice Expense"), default = False)
    addToInvoicePart = models.BooleanField(_("Add To Invoice Part"), default = False)
    
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    paidPrice = models.FloatField(_("Paid Price"), default = 0, blank = True, null = True)
    
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "service_send_invoice_currency", default = 106, blank = True, null = True)
    
    #serviceCards = models.ManyToManyField(OfferServiceCard,related_name='service_send_invoices',through='ServiceSendInvoiceServiceCard', blank = True, null=True)
    #expenses = models.ManyToManyField(OfferExpense,related_name='service_send_invoices',through='ServiceSendInvoiceExpense', blank = True, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.sendInvoiceNo)
    
class ServiceSendInvoiceServiceCard(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="service_send_invoice_service_card_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(ServiceSendInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    offerServiceCard = models.ForeignKey(OfferServiceCard, on_delete=models.CASCADE, related_name = "service_send_invoice_service_card_service_card", blank = True)
    quantity = models.FloatField(default=1)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(ServiceSendInvoiceServiceCard, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.offerServiceCard.serviceCard.code)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['offerServiceCard', 'invoice'], name='unique_offerServiceCard_invoice')
        ]
        
class ServiceSendInvoiceExpense(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="service_send_invoice_expense_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(ServiceSendInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    offerExpense = models.ForeignKey(OfferExpense, on_delete=models.CASCADE, related_name = "service_send_invoice_expense_expense", blank = True)
    quantity = models.FloatField(default=1)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(ServiceSendInvoiceExpense, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.offerExpense.expense.code)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['offerExpense', 'invoice'], name='unique_offerExpense_invoice')
        ]
        
class ServiceSendInvoicePart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="service_send_invoice_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(ServiceSendInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    offerPart = models.ForeignKey(OfferPart, on_delete=models.CASCADE, related_name = "service_send_invoice_expense_expense", blank = True)
    quantity = models.FloatField(default=1)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(ServiceSendInvoicePart, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.offerPart.part.partNo)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['offerPart', 'invoice'], name='unique_offerPart_invoice')
        ]
  
class ProformaInvoice(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="proforma_invoice_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name="proforma_invoice", blank = True, null = True, )
    theRequest = models.ForeignKey(Request, on_delete=models.SET_NULL, blank = True, null = True, related_name="proforma_invoice_request")
    orderConfirmation = models.ForeignKey(OrderConfirmation, on_delete=models.SET_NULL, blank = True, null = True, related_name="proforma_invoice_order_confirmation")
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, blank = True, null = True, related_name="proforma_invoice_offer")
    
    seller = models.ForeignKey(SourceCompany, on_delete=models.DO_NOTHING, related_name="proforma_invoice_seller", blank = True, null = True)
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="proforma_invoice_customer", blank = True, null = True)
    vessel = models.ForeignKey(Vessel, on_delete=models.DO_NOTHING, related_name="proforma_invoice_vessel", blank = True, null = True)
    billing = models.ForeignKey(Billing, on_delete=models.DO_NOTHING, related_name="proforma_invoice_billing", blank = True, null = True)
    
    GROUPS = (
        ('order', _('Order')),
        ('service', _('Service')),
    )
    
    group = models.CharField(max_length=30, choices=GROUPS, default = "order", blank=True, null=True)
    
    awb = models.CharField(_("AWB"), max_length=140, blank = True, null=True)
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Proforma Year"), max_length=140, blank = True, null = True)
    code = models.IntegerField(_("Proforma Code"), blank = True, null = True)
    proformaInvoiceNo = models.CharField(_("Proforma Invoice No"), max_length=140, blank = True, null=True)
    
    proformaInvoiceDate = models.DateField(_("Proforma Invoice Date"), default = timezone.now, blank = True)
    
    paymentDate = models.DateField(_("Payment Date"), default = timezone.now, blank = True)

    deliveryDate = models.DateField(_("Delivery Date"), null = True, blank = True)
    deliveryNo = models.CharField(_("Delivery No"), max_length=140, blank = True, null=True)
    
    careOf = models.CharField(_("Care Of"), max_length=250, blank = True, null = True)
    transport = models.CharField(_("Transport"), max_length=250, blank = True, null = True)
    
    ready = models.BooleanField(_("Ready"), default = False)
    payed = models.BooleanField(_("Payed"), default = False)
    
    discountPrice = models.FloatField(_("Discount Price"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    netPrice = models.FloatField(_("Net Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    paidPrice = models.FloatField(_("Paid Price"), default = 0, blank = True, null = True)
    exchangeRate = models.FloatField(_("Exchange Rate"), default = 0, blank = True, null = True)
    only = models.CharField(_("Onyl"), max_length=500, blank = True, null = True)
    
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "proforma_invoice_currency", default = 106, blank = True, null = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.proformaInvoiceNo)

class ProformaInvoiceItem(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="proforma_invoice_item_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(ProformaInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    trDescription = models.TextField(_("Turkish Description"), max_length=250, null=True, blank = True)
    
    quotationPart = models.ForeignKey(QuotationPart, on_delete=models.DO_NOTHING, related_name = "proforma_invoice_quotation_part", blank = True, null = True)
    offerServiceCard = models.ForeignKey(OfferServiceCard, on_delete=models.DO_NOTHING, related_name = "proforma_invoice_offer_service_card", blank = True, null = True)
    offerPart = models.ForeignKey(OfferPart, on_delete=models.DO_NOTHING, related_name = "proforma_invoice_offer_part", blank = True, null = True)
    offerExpense = models.ForeignKey(OfferExpense, on_delete=models.DO_NOTHING, related_name = "proforma_invoice_offer_expense", blank = True, null = True)
    
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "proforma_invoice_part", blank = True, null = True)
    serviceCard = models.ForeignKey(ServiceCard, on_delete=models.CASCADE, related_name = "proforma_invoice_service_card", blank = True, null = True)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name = "proforma_invoice_expense", blank = True, null = True)
    
    name = models.CharField(_("Expense Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    UNITS = (
        ('day', _('Day')),
        ('hrs', _('HRS')),
        ('kg', _('Kg')),
        ('m²', _('m²')),
        ('mm', _('MM')),
        ('pc', _('Pc')),
        ('pcs', _('PCS')),
        ('pk', _('PK')),
        ('persons', _('Persons')),
    )
    unit = models.CharField(_("Units"), max_length=40, default = "pc", choices = UNITS)
    
    quantity = models.FloatField(default=1)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(ProformaInvoiceItem, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)
 
class ProformaInvoicePart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="proforma_invoice_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(ProformaInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    quotationPart = models.ForeignKey(QuotationPart, on_delete=models.CASCADE, related_name = "proforma_invoice_part_part", blank = True)
    quantity = models.FloatField(default=1)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(ProformaInvoicePart, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.quotationPart.inquiryPart.requestPart.part.partNo)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['quotationPart', 'invoice'], name='unique_quotationPart_proforma_invoice')
        ]
        
class ProformaInvoiceExpense(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="proforma_invoice_exepnse_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(ProformaInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, blank = True, null = True)
    
    UNITS = (
        ('day', _('Day')),
        ('hrs', _('HRS')),
        ('kg', _('Kg')),
        ('m²', _('m²')),
        ('mm', _('MM')),
        ('pc', _('Pc')),
        ('pcs', _('PCS')),
        ('pk', _('PK')),
        ('persons', _('Persons')),
    )
    
    unit = models.CharField(_("Units"), default = "pc", max_length=40, choices = UNITS)
    
    name = models.CharField(_("Billing Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500,blank=True, null=True)
    
    quantity = models.FloatField(default=1)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

class CommericalInvoice(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="commerical_invoice_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name="commerical_invoice", blank = True, null = True, )
    theRequest = models.ForeignKey(Request, on_delete=models.SET_NULL, blank = True, null = True, related_name="commerical_invoice_request")
    orderTracking = models.ForeignKey(OrderTracking, on_delete=models.SET_NULL, blank = True, null = True, related_name="commerical_invoice_order_tracking")
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Commerical Invoice Year"), max_length=140, blank = True, null = True)
    code = models.IntegerField(_("Commerical Invoice Code"), blank = True, null = True)
    sendInvoiceNoSys = models.CharField(_("Commerical Invoice No"), max_length=140, blank = True, null=True)
    
    seller = models.ForeignKey(SourceCompany, on_delete=models.DO_NOTHING, related_name="commerical_invoice_seller", blank = True, null = True)
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="commerical_invoice_customer", blank = True, null = True)
    vessel = models.ForeignKey(Vessel, on_delete=models.DO_NOTHING, related_name="commerical_invoice_vessel", blank = True, null = True)
    billing = models.ForeignKey(Billing, on_delete=models.DO_NOTHING, related_name="commerical_invoice_billing", blank = True, null = True)
    
    customerName = models.CharField(_("Customer Name"), max_length=140, blank = True, null=True)
    projectNo = models.CharField(_("Project No"), max_length=140, blank = True, null=True)
    
    GROUPS = (
        ('order', _('Order')),
        ('service', _('Service')),
    )
    
    group = models.CharField(max_length=30, choices=GROUPS, default = "order", blank=True, null=True)
    
    awb = models.CharField(_("AWB"), max_length=140, blank = True, null=True)
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    
    commericalInvoiceNo = models.CharField(_("Commerical Invoice No"), max_length=140, unique = True, blank = True, null=True)
    
    commericalInvoiceDate = models.DateField(_("Commerical Invoice Date"), default = timezone.now, blank = True)
    
    paymentDate = models.DateField(_("Payment Date"), default = timezone.now, blank = True)

    deliveryDate = models.DateField(_("Delivery Date"), null = True, blank = True)
    deliveryNo = models.CharField(_("Delivery No"), max_length=140, blank = True, null=True)
    deliveryNote = models.TextField(_("Delivery Note"), max_length=500, blank = True, null = True)
    
    transport = models.CharField(_("Transport"), max_length=250, blank = True, null = True)
    
    ready = models.BooleanField(_("Ready"), default = False)
    
    discountPrice = models.FloatField(_("Discount Price"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    netPrice = models.FloatField(_("Net Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    exchangeRate = models.FloatField(_("Exchange Rate"), default = 0, blank = True, null = True)
    
    only = models.CharField(_("Only"), max_length=500, blank = True, null = True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "commerical_invoice_currency", default = 106, blank = True, null = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.commericalInvoiceNo)

class CommericalInvoiceItem(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="commerical_invoice_item_ource_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(CommericalInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    trDescription = models.TextField(_("Turkish Description"), max_length=250, null=True, blank = True)
    
    quotationPart = models.ForeignKey(QuotationPart, on_delete=models.DO_NOTHING, related_name = "commerical_invoice_quotation_part", blank = True, null = True)
    offerServiceCard = models.ForeignKey(OfferServiceCard, on_delete=models.DO_NOTHING, related_name = "commerical_invoice_offer_service_card", blank = True, null = True)
    
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "commerical_invoice_part", blank = True, null = True)
    serviceCard = models.ForeignKey(ServiceCard, on_delete=models.CASCADE, related_name = "commerical_invoice_service_card", blank = True, null = True)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name = "commerical_invoice_expense", blank = True, null = True)
    
    name = models.CharField(_("Expense Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    UNITS = (
        ('day', _('Day')),
        ('hrs', _('HRS')),
        ('kg', _('Kg')),
        ('m²', _('m²')),
        ('mm', _('MM')),
        ('pc', _('Pc')),
        ('pcs', _('PCS')),
        ('pk', _('PK')),
        ('persons', _('Persons')),
    )
    unit = models.CharField(_("Units"), max_length=40, default = "pc", choices = UNITS)
    
    quantity = models.FloatField(default=1)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(CommericalInvoiceItem, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)

class CommericalInvoiceExpense(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="commerical_invoice_expense_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    invoice = models.ForeignKey(CommericalInvoice, on_delete=models.CASCADE, blank = True, null = True)
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, blank = True, null = True)
    
    UNITS = (
        ('day', _('Day')),
        ('hrs', _('HRS')),
        ('kg', _('Kg')),
        ('m²', _('m²')),
        ('mm', _('MM')),
        ('pc', _('Pc')),
        ('pcs', _('PCS')),
        ('pk', _('PK')),
        ('persons', _('Persons')),
    )
    
    unit = models.CharField(_("Units"), default = "pc", max_length=40, choices = UNITS)
    
    name = models.CharField(_("Billing Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500,blank=True, null=True)
    
    quantity = models.FloatField(default=1)
    
    unitPrice = models.FloatField(_("Unit Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    vatPrice = models.FloatField(_("Vat Price"), default = 0, blank = True, null = True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

class Process(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="process_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="process_customer", blank = True, null = True)
    incomingInvoice = models.ForeignKey(IncomingInvoice, on_delete=models.CASCADE, related_name="process_incoming_invoice", blank = True, null = True)
    sendInvoice = models.ForeignKey(SendInvoice, on_delete=models.CASCADE, related_name="process_send_invoice", blank = True, null = True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="process_payment", blank = True, null = True)
    
    companyName = models.CharField(_("Company Name"), max_length=140, blank = True, null=True)
    sourceNo = models.CharField(_("Source No"), max_length=140, blank = True, null=True)
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "PRC", blank = True, null=True)
    yearCode = models.CharField(_("Payment Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Payment Code"), max_length=140, blank = True, null = True)
    processNo = models.CharField(_("Payment No"), max_length=140, blank = True, null=True)
    
    PROCESS_TYPES = (
        ('incoming_invoice', _('Incoming Invoice')),
        ('send_invoice', _('Send Invoice')),
        ('payment_in', _('Payment In')),
        ('payment_out', _('Payment Out')),
    )
    
    type = models.CharField(max_length=30, choices=PROCESS_TYPES, default = "send_invoice")
    
    processDate = models.DateField(_("Process Date"), default = timezone.now, blank = True)
    processDateTime = models.DateTimeField(_("Process Date Time"), default = timezone.now, blank = True)
    
    amount = models.FloatField(_("Amount"), default = 0, blank = True, null = True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "process_currency", default = 106, blank = True, null = True)

    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.processNo)

class ProcessStatus(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="process_status_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name="process_status_project", blank = True, null = True, )
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, blank = True, null = True, related_name="process_status_offer")
    purchasingProject = models.ForeignKey(PurchasingProject, on_delete=models.SET_NULL, blank = True, null = True, related_name="process_status_purchasing_project")
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "PS", blank = True, null=True)
    yearCode = models.CharField(_("Payment Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Payment Code"), max_length=140, blank = True, null = True)
    processStatusNo = models.CharField(_("Process Status No"), max_length=140, blank = True, null=True)
    
    PROCESS_STATUS_TYPES = (
        ('order', _('Order')),
        ('service', _('Service')),
        ('purchasing', _('Purchasing')),
    )
    
    type = models.CharField(max_length=30, choices=PROCESS_STATUS_TYPES, default = "order")
    
    processStatusDate = models.DateField(_("Process Status Date"), default = timezone.now, blank = True)
    processStatusDateTime = models.DateTimeField(_("Process Status Date Time"), default = timezone.now, blank = True)

    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.processStatusNo)