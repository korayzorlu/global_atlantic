import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
# Create your models here.
from simple_history.models import HistoricalRecords
from django.db.models.signals import pre_save
from django.dispatch import receiver

from ckeditor.fields import RichTextField
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model

from card.models import Company, Vessel, Person, Currency, Country, City
from data.models import Maker, MakerType, Part

from decimal import Decimal, ROUND_UP

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="unknown")[0]

def order_tracking_document_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    return 'docs/{2}/sale/order_tracking/documents/{0}/{1}'.format(instance.orderTracking.project.projectNo, filename,instance.sourceCompany.id)

class Project(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="project_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user))
    
    PROJECT_STAGES = (
        ('request', _('Request')),
        ('inquiry', _('Inquiry')),
        ('quotation', _('Quotation')),
        ('order_confirmation', _('Order Confirmation')),
        ('order_not_confirmation', _('Order Not Confirmation')),
        ('purchase_order', _('Purchase Order')),
        ('order_tracking', _('Order Tracking')),
        ('invoiced', _('Invoiced')),
    )
    
    stage = models.CharField(_("Stage"), max_length=40, default="", blank= True, null=True, choices = PROJECT_STAGES)
    
    STATUSSES = (
        ('request', _('Request')),
        ('inquiry', _('Inquiry')),
        ('quotation', _('Quotation')),
        ('order_confirmation', _('Order Confirmation')),
        ('order_in_process', _('Order In Process')),
    )
    
    projectNo = models.CharField(_("Project No"), max_length=140, unique=False, null=True, db_index = True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.projectNo)

    class Meta:
        ordering = ['projectNo']
        
class Request(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="request_source_company")
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True, blank = True, related_name="request")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Request Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Request Code"), max_length=140, blank = True, null = True)
    requestNo = models.CharField(_("Request No"), max_length=140, blank = True, null=True, db_index = True)
    
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
    vessel = models.ForeignKey(Vessel, on_delete=models.DO_NOTHING, blank = True, null = True)
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank = True, null = True)
    vesselPerson = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank = True, null = True, related_name="request_vessel_person")
    customerRef = models.CharField(_("Customer Ref"), max_length=140, blank = True, null=True)
    note = models.CharField(_("Note"), max_length=150, blank = True, null=True)
    
    maker = models.ForeignKey(Maker, on_delete=models.DO_NOTHING, related_name = "request_maker", blank = True, null = True)
    makerType = models.ForeignKey(MakerType, on_delete=models.DO_NOTHING, related_name = "request_maker_type", blank = True, null = True)
    
    #parts = models.ManyToManyField(Part,related_name='requests',through='RequestPart', blank = True, null=True)
    
    requestDate = models.DateField(_("Request Date"), default = timezone.now, blank = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.requestNo)

    class Meta:
        ordering = ['requestDate']

class RequestPart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="request_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    theRequest = models.ForeignKey(Request, on_delete=models.CASCADE, blank = True, null = True)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
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
    
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "request_part_part")
    quantity = models.FloatField(default=1)
    
    def save(self, *args, **kwargs):

        
        super(RequestPart, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.part.partNo)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['part', 'theRequest'], name='unique_part_theRequest')
    #     ]
        
        
class Inquiry(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="inquiry_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="inquiry_user")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank = True,related_name="inquiry")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    theRequest = models.ForeignKey(Request, on_delete=models.CASCADE, blank = True, null = True, related_name="inquiry_request")
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Request Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Request Code"), max_length=140, blank = True, null = True)
    inquiryNo = models.CharField(_("Inquiry No"), max_length=140, blank = True, null=True, db_index = True)
    
    supplier = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
    # customer = models.CharField(_("Customer"), max_length=140, null=True, blank = True)
    # vessel = models.CharField(_("Vessel"), max_length=140, null=True, blank = True)
    
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank = True, null=True)
    supplierRef = models.CharField(_("Supplier Ref"), max_length=140, blank = True, null=True)
    payment = models.CharField(_("Payment"), max_length=140, blank = True, null=True)
    
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "inquiry_part_currency", default = 106, blank = True, null = True)
    
    parts = models.ManyToManyField(RequestPart,related_name='inquiries',through='InquiryPart', blank = True)
    
    note = models.TextField(_("Note"), max_length = 500, blank = True, null = True)
    
    totalTotalPrice = models.FloatField(_("Total Total Prince"), default = 0, blank = True, null = True)
    
    inquiryDate = models.DateField(_("Inquiry Date"), default = timezone.now, blank = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.inquiryNo)

    class Meta:
        ordering = ['inquiryDate']
        
class InquiryPart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="inquriy_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, blank = True, null = True)
    
    AVAILABILITIES = (
        ('day', _('Day')),
        ('week', _('Week')),
        ('tba', _('TBA')),
        ('ex_stock', _('Ex Stock')),
        ('ex_stock_istanbul', _('Ex Stock Istanbul')),
    )
    
    availabilityType = models.CharField(max_length=30, choices=AVAILABILITIES, default='day', blank=True, null=True)
    availability = models.IntegerField(_("Availability"), default=0, blank=True, null=True)
    
    maker = models.ForeignKey(Maker, on_delete=models.DO_NOTHING, related_name = "inquiry_part_maker", blank = True, null = True)
    makerType = models.ForeignKey(MakerType, on_delete=models.DO_NOTHING, related_name = "inquiry_part_maker_type", blank = True, null = True)
    
    requestPart = models.ForeignKey(RequestPart, on_delete=models.CASCADE, related_name = "inquiry_part_part", blank = True)
    quantity = models.FloatField(default=1)
    
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
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Prince"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Prince"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), max_length=1000, blank = True, null = True)
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(InquiryPart, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.requestPart.part.partNo)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['requestPart', 'inquiry'], name='unique_requestPart_inquiry')
        ]
   
class Quotation(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="quotation_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="quotation_user")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank = True,related_name="quotation")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, blank = True, null = True, related_name="quotation_inquiry")
    inquiries = models.ManyToManyField(Inquiry,related_name='inquiries', blank = True)
    soc = models.CharField(_("SOC"), max_length=140, blank = True, null = True)
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Request Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Request Code"), max_length=140, blank = True, null = True)
    quotationNo = models.CharField(_("Quotation No"), max_length=140, blank = True, null=True, db_index = True)
    
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank = True, null=True)
    
    validity = models.CharField(_("Validity"), max_length=140, blank = True, null = True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "quotation_part_currency", default = 106, blank = True, null = True)
    
    PAYMENTS = (
        ('as_agreed', _('As Agreed')),
        ('as_advanced', _('As Advanced')),
        ('as_credit', _('As Credit')),
    )
    
    payment = models.CharField(max_length=30, blank = True, null = True)
    delivery = models.CharField(_("Delivery"), max_length=140, blank = True, null = True)
    remark = models.CharField(_("Remark"), max_length=140, blank = True, null = True)
    
    parts = models.ManyToManyField(InquiryPart,related_name='quotations',through='QuotationPart', blank = True)
    
    note = models.TextField(_("Note"), max_length = 500,
                            default = "VAT EXCLUDED - TRANSPORTATION&PACKING AND CUSTOMS COSTS ARE NOT INCLUDED\nABOVE OFFERED PRICES ARE VALID FOR COMPLETE ORDER ONLY.",
                            blank = True, null = True)
    
    APPROVES = (
        ('notSent', _('Not Sent For Approval')),
        ('sent', _('Sent For Approval')),
        ('approved', _('Approved By Manager')),
        ('notApproved', _('Not Approved By Manager')),
        ('notified', _('Notified')),
        ('notNotified', _('Not Notified')),
        ('revised', _('Revised')),
    )
    
    approval = models.CharField(max_length=30, choices=APPROVES, default = "notSent", blank = True, null = True)
    
    APPROVAL_CLASSES = (
        ('assistant', _('Assistant')),
        ('specialist', _('Specialist')),
        ('executivor', _('Executivor')),
        ('director', _('Director')),
        ('generalManager', _('General Manager')),
    )
    
    approvalClass = models.CharField(max_length=30, choices=APPROVAL_CLASSES, default = "assistant", blank = True, null = True)
    
    DELIVERY_STATUSES = (
        ('noStatus', _('No Status')),
        ('billing', _('Billing')),
    )
    
    deliveryStatus = models.CharField(max_length=30, choices=DELIVERY_STATUSES, default = "noStatus", blank = True, null = True)
    
    manuelDiscount = models.FloatField(_("Manuel Discount"), default = 0, blank = True, null = True)
    manuelDiscountAmount = models.FloatField(_("Manuel Discount Amount"), default = 0, blank = True, null = True)
    
    totalDiscountPrice = models.FloatField(_("Total Discount Prince"), default = 0, blank = True, null = True)
    totalBuyingPrice = models.FloatField(_("Total Buying Prince"), default = 0, blank = True, null = True)
    totalSellingPrice = models.FloatField(_("Total Selling Prince"), default = 0, blank = True, null = True)
    
    quotationDate = models.DateField(_("Quotation Date"), default = timezone.now, blank = True)
    
    revised = models.BooleanField(_("Revised"), default = False)
    rev = models.BooleanField(_("Revise"), default = False)
    revNo = models.IntegerField(_("Revision No"), default = 0, blank = True, null = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.quotationNo)

    class Meta:
        ordering = ['quotationDate']
        
class QuotationPart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="quotation_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True, db_index=True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, blank = True, null = True, db_index=True)
    
    AVAILABILITIES = (
        ('day', _('Day')),
        ('week', _('Week')),
        ('tba', _('TBA')),
        ('ex_stock', _('Ex Stock')),
        ('ex_stock_istanbul', _('Ex Stock Istanbul')),
    )
    
    availabilityType = models.CharField(max_length=30, choices=AVAILABILITIES, default='day', blank=True, null=True)
    availability = models.IntegerField(_("Availability"), blank=True, null=True)
    availabilityChar = models.CharField(_("Availability"), max_length=30, blank=True, null=True)
    
    maker = models.ForeignKey(Maker, on_delete=models.DO_NOTHING, related_name = "quotation_part_maker", blank = True, null = True)
    makerType = models.ForeignKey(MakerType, on_delete=models.DO_NOTHING, related_name = "quotation_part_maker_type", blank = True, null = True)
    
    inquiryPart = models.ForeignKey(InquiryPart, on_delete=models.CASCADE, related_name = "quotaiton_part_part", blank = True)
    quantity = models.FloatField(_("Quantity"), default = 1, blank = True, null = True)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice1 = models.FloatField(_("Unit Prince 1"), default = 0, blank = True, null = True)
    totalPrice1 = models.FloatField(_("Total Prince 1"), default = 0, blank = True, null = True)
    
    unitPrice2 = models.FloatField(_("Unit Prince 2"), default = 0, blank = True, null = True)
    totalPrice2 = models.FloatField(_("Total Prince 2"), default = 0, blank = True, null = True)
    
    unitPrice3 = models.FloatField(_("Unit Prince 3"), default = 0, blank = True, null = True)
    totalPrice3 = models.FloatField(_("Total Prince 3"), default = 0, blank = True, null = True)
    
    profit = models.FloatField(_("Profit"), default = 0, blank = True, null = True)
    discount = models.FloatField(_("Discount"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), max_length=1000, blank = True, null = True)
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)
    
    alternative = models.BooleanField(_("Alternative"), default = False)
    
    def save(self, *args, **kwargs):
        #self.totalPrice1 = float(self.unitPrice1) * int(self.quantity)
        
        
        
        
        super(QuotationPart, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.inquiryPart.requestPart.part.partNo)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['inquiryPart', 'quotation'], name='unique_inquiryPart_quotation')
    #     ]

class QuotationExtra(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="quotation_extra_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, blank = True, null = True)
    
    name = models.CharField(_("Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500,blank=True, null=True)

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
    
    unitPrice = models.FloatField(_("Unit Prince"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Prince"), default = 0, blank = True, null = True)
    quantity = models.FloatField(_("Quantity"), default = 1, blank = True, null = True)


    def __str__(self):
        return str(self.description)

    class Meta:
        ordering = ['description']
    
class OrderConfirmation(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="order_confirmation_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="order_confirmation_user")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank = True,related_name="order_confirmation")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE, blank = True, null = True, related_name="order_confirmation_quotation")
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Order Confirmation Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Order Confirmation Code"), max_length=140, blank = True, null = True)
    orderConfirmationNo = models.CharField(_("Order Confirmation No"), max_length=140, blank = True, null=True, db_index = True)
    
    ORDER_STATUSES = (
        ('collecting', _('Collecting')),
        ('collected', _('Collected')),
        ('invoiced', _('Invoiced')),
        ('logistic', _('Logistic')),
        ('project_closed', _('Project Closed')),
    )
    
    status = models.CharField(_("Order Status"), max_length=50, choices = ORDER_STATUSES, blank = True, default='collecting')
    
    invoiced = models.BooleanField(_("Invoiced"), default = False)
    sendInvoiced = models.BooleanField(_("Send Invoiced"), default = False)
    proformaInvoiced = models.BooleanField(_("Proforma Invoiced"), default = False)
    
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), blank = True, null = True)
    
    orderConfirmationDate = models.DateField(_("Order Confirmation Date"), default = timezone.now, blank = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.orderConfirmationNo)

    class Meta:
        ordering = ['orderConfirmationDate']

class Reason(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="reason_source_company")
    name = models.CharField(max_length=140, blank = True, null=True)

    def __str__(self):
        return self.name
     
class OrderNotConfirmation(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="order_notconfirmation_source_company")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank = True,related_name="order_not_confirmation")
    quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE, blank = True, null = True, related_name="order_not_confirmation_quotation")
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Order Not Confirmation Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Order Not Confirmation Code"), max_length=140, blank = True, null = True)
    orderNotConfirmationNo = models.CharField(_("Order Not Confirmation No"), max_length=140, blank = True, null=True)
    
    delay = models.CharField(_("Delay"), max_length=140, blank = True, null = True)
    
    ORDER_PROCESS_TYPES = (
        ('email', _('Email')),
        ('phone', _('Phone')),
        ('verbal', _('Verbal')),
    )
    
    orderProcessType = models.CharField(_("Order Process Type"), max_length=50, choices = ORDER_PROCESS_TYPES, default='email')
    
    CUSTOMER_REACTIONS = (
        ('OS', _('Optimistic and Satisfied')),
        ('HU', _('Harsh and Unsatisfied')),
        ('CN', _('Calm and Normal')),
    )
    
    customerReaction = models.CharField(_("Customer Reaction"), max_length=50, choices=CUSTOMER_REACTIONS, default='OS')
    
    FINAL_DECISIONS = ((True, 'Yes, order will not be fulfilled'), (False, 'No, order pending'))
    
    finalDecision = models.BooleanField(_("Final Decision"),choices = FINAL_DECISIONS, default=False)
    
    reasons = models.ManyToManyField(Reason,related_name='reasons', blank = True)
    
    suggestion = models.TextField(_("Suggestion"), blank = True, null = True)
    
    orderNotConfirmationDate = models.DateField(_("Order Not Confirmation Date"), default = timezone.now, blank = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.orderNotConfirmationNo)

    class Meta:
        ordering = ['orderNotConfirmationDate']
        
class PurchaseOrder(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="purchase_order_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="purchase_order_user")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank = True,related_name="purchase_order")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, blank = True, null = True, related_name="purchase_order_inquiry")
    orderConfirmation = models.ForeignKey(OrderConfirmation, on_delete=models.CASCADE, blank = True, null = True, related_name="purchase_order_order_confirmation")
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "ESO", blank = True, null=True)
    yearCode = models.CharField(_("Purchase Order Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Purchase Order Code"), max_length=140, blank = True, null = True)
    purchaseOrderNo = models.CharField(_("Purchase Order No"), max_length=140, blank = True, null=True, db_index = True)
    
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "purchase_order_currency", default = 106, blank = True, null = True)
    
    PAYMENTS = (
        ('1_month', _('1 Month')),
        ('1_week', _('1 Week')),
        ('2_month', _('2 Month')),
        ('2_week', _('2 Week')),
        ('3_month', _('3 Month')),
        ('3_week', _('3 Week')),
        ('as_agreed', _('As Agreed')),
    )
    payment = models.CharField(max_length=30, blank = True, null = True)
    delivery = models.CharField(_("Delivery"), max_length=140, blank = True, null = True)
    discount = models.FloatField(_("Discount"), default = 0, blank = True, null = True)
    discountAmount = models.FloatField(_("Discount Amount"), default = 0, blank = True, null = True)
    
    totalDiscountPrice = models.FloatField(_("Total Discount Prince"), default = 0, blank = True, null = True)
    totalTotalPrice = models.FloatField(_("Total Prince"), default = 0, blank = True, null = True)
    
    rate = models.CharField(_("Rate"), max_length=140, blank = True, null = True)
    
    invoiced = models.BooleanField(_("Invoiced"), default = False)
    incomingInvoiced = models.BooleanField(_("Incoming Invoiced"), default = False)
    
    parts = models.ManyToManyField(InquiryPart,related_name='purchaseOrders',through='PurchaseOrderPart', blank = True)
    
    orderDueDate = models.DateField(_("Order Due Date"), default = timezone.now, blank = True)
    
    purchaseOrderDate = models.DateField(_("Purchase Order Date"), default = timezone.now, blank = True)
    
    note = models.TextField(_("Note"), max_length = 500, blank = True, null = True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.purchaseOrderNo)

    class Meta:
        ordering = ['purchaseOrderDate']
        
class PurchaseOrderPart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="purchase_order_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    purchaseOrder = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, blank = True, null = True)
    
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
    
    AVAILABILITIES = (
        ('day', _('Day')),
        ('week', _('Week')),
        ('tba', _('TBA')),
        ('ex_stock', _('Ex Stock')),
        ('ex_stock_istanbul', _('Ex Stock Istanbul')),
    )
    
    availabilityType = models.CharField(max_length=30, choices=AVAILABILITIES, default='day', blank=True, null=True)
    availability = models.IntegerField(_("Availability"), blank=True, null=True)
    
    maker = models.ForeignKey(Maker, on_delete=models.DO_NOTHING, related_name = "purchaseOrder_part_maker", blank = True, null = True)
    makerType = models.ForeignKey(MakerType, on_delete=models.DO_NOTHING, related_name = "purchaseOrder_part_maker_type", blank = True, null = True)
    
    QUALITIES = (
        ('bosch', _('Bosch')),
        ('daros', _('Daros')),
        ('duap', _('Duap')),
    )
    
    quality = models.CharField(max_length=30, choices=QUALITIES, blank=True, null=True)
    
    ORDER_TYPES = (
        ('stock_order', _('Stock Order')),
        ('customer_order', _('Customer Order')),
    )
    
    orderType = models.CharField(max_length=30, choices=ORDER_TYPES, blank=True, null=True)
    
    inquiryPart = models.ForeignKey(InquiryPart, on_delete=models.CASCADE, related_name = "purchaseOrder_part_part", blank = True)
    quantity = models.FloatField(_("Quantity"), default = 1, blank = True, null = True)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Prince"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Prince"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), max_length=1000, blank = True, null = True)
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        self.totalPrice = float(self.unitPrice) * float(self.quantity)
        
        super(PurchaseOrderPart, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.partNo)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['inquiryPart', 'purchaseOrder'], name='unique_inquiryPart_purchaseOrder')
        ]
        
class OrderTracking(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="order_tracking_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="order_tracking_user")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank = True,related_name="order_tracking")
    theRequest = models.ForeignKey(Request, on_delete=models.CASCADE, blank = True, null = True, related_name="order_tracking_request")
    purchaseOrders = models.ManyToManyField(PurchaseOrder,related_name='purchase_orders', blank = True)
    
    collections = models.ManyToManyField(PurchaseOrder,related_name='order_trackings',through='Collection', blank = True)
    
    orderTrackingNo = models.CharField(_("Order Tracking No"), max_length=140, blank = True, null=True)
    collected = models.BooleanField(_("Collected"), default = False)
    invoiced = models.BooleanField(_("Invoiced"), default = False)
    delivered = models.BooleanField(_("Delivered"), default = False)
    sendInvoiced = models.BooleanField(_("Send Invoiced"), default = False)
    
    items = models.JSONField(_("Items"), blank = True, null = True)
    
    orderTrackingDate = models.DateField(_("Order Tracking Date"), default = timezone.now, blank = True)
    
    note = models.TextField(_("Note"), blank = True, null = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.project.projectNo)

    class Meta:
        ordering = ['orderTrackingDate']

class OrderTrackingDocument(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="order_tracking_document_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    orderTracking = models.ForeignKey(OrderTracking, on_delete=models.CASCADE, blank = True, null = True)
    
    file = models.FileField(_("File"), blank =True, null = True, upload_to = order_tracking_document_directory_path)
    name = models.CharField(_("File Name"), max_length=140, blank = True, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        
        if self.file:
            self.name = os.path.basename(self.file.name)
        
        super(OrderTrackingDocument, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)

class Collection(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="collection_source_company")
    orderTracking = models.ForeignKey(OrderTracking, on_delete=models.CASCADE, blank = True, null = True)
    purchaseOrder = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, blank = True, null = True)
    
    trackingNo = models.CharField(_("Tracking No"), max_length=140, blank = True, null=True)
    
    port = models.CharField(_("Port"), max_length=50, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, blank = True, null=True)
    eta = models.CharField(_("ETA"), max_length=140, blank=True, null=True)
    transportationCompany = models.CharField(_("Transportation Company"), max_length=140, blank=True, null=True)
    waybillNo = models.CharField(_("Waybill No"), max_length=140, blank=True, null=True)
    insuranceCompany = models.CharField(_("Insurance Company"), max_length=140, blank=True, null=True)
    insuranceFileNo = models.CharField(_("Insurance File No"), max_length=140, blank=True, null=True)
    
    agent = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name = "collection_agent", blank = True, null = True)
    agentChar = models.CharField(_("Agent"), max_length=140, blank=True, null=True)
    address = models.TextField(_("Address"), max_length=500,blank=True, null=True)
    pic = models.CharField(_("PIC"), max_length=140, blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=140, blank=True, null=True)
    weight = models.CharField(_("Weight"), max_length=140, blank=True, null=True)
    fax = models.CharField(_("Fax"), max_length=140, blank=True, null=True)
    dimensions = models.CharField(_("Dimensions"), max_length=140, blank=True, null=True)
    email = models.CharField(_("Email"), max_length=140, blank=True, null=True)
    
    dispatchDate = models.DateField(_("Dispatch Date"), default = timezone.now, blank = True)
    deliveryDate = models.DateField(_("Delivery Date"), default = timezone.now, blank = True)
    
    buyingTransportation = models.FloatField(_("Buying Transportation"), default = 0, blank = True, null = True)
    buyingTransportationCurrency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "buying_transportation_currency", default = 106, blank = True, null = True)
    buyingPacking = models.FloatField(_("Buying Packing"), default = 0, blank = True, null = True)
    buyingPackingCurrency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "buying_packing_currency", default = 106, blank = True, null = True)
    buyingInsurance = models.FloatField(_("Buying Insurance"), default = 0, blank = True, null = True)
    buyingInsuranceCurrency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "buying_insurance_currency", default = 106, blank = True, null = True)
    
    note = models.TextField(_("Note"), blank = True, null = True)
    
    #parts = models.ManyToManyField(PurchaseOrderPart,related_name='collections',through='CollectionPart', blank = True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['purchaseOrder', 'orderTracking'], name='unique_purchaseOrder_orderTracking')
        ]


class CollectionPart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="collection_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, blank = True, null = True)
    
    purchaseOrderPart = models.ForeignKey(PurchaseOrderPart, on_delete=models.CASCADE, related_name = "collection_part_part", blank = True)
    quantity = models.FloatField(_("Quantity"), default = 1, blank = True, null = True)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    tracked = models.IntegerField(_("Tracked"), default = 0, blank=True, null=True)
    remaining = models.IntegerField(_("Remaining"), default = 0, blank=True, null=True)

    dispatched = models.BooleanField(_("Dispatched"), default = False)
    
    trackedDate = models.DateField(_("Tracked Date"), default = timezone.now, blank = True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.purchaseOrderPart.inquiryPart.requestPart.part.partNo)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['purchaseOrderPart', 'collection'], name='unique_purchaseOrderPart_collection')
        ]
        
class Delivery(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="delivery_source_company")
    orderTracking = models.ForeignKey(OrderTracking, on_delete=models.CASCADE, blank = True, null = True)
    orderConfirmation = models.ForeignKey(OrderConfirmation, on_delete=models.CASCADE, blank = True, null = True)

    trackingNo = models.CharField(_("Tracking No"), max_length=140, blank = True, null=True)
    
    port = models.CharField(_("Port"), max_length=50, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, blank = True, null=True)
    eta = models.CharField(_("ETA"), max_length=140, blank=True, null=True)
    transportationCompany = models.CharField(_("Transportation Company"), max_length=140, blank=True, null=True)
    waybillNo = models.CharField(_("Waybill No"), max_length=140, blank=True, null=True)
    insuranceCompany = models.CharField(_("Insurance Company"), max_length=140, blank=True, null=True)
    insuranceFileNo = models.CharField(_("Insurance File No"), max_length=140, blank=True, null=True)
    
    agent = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name = "delivery_agent", blank = True, null = True)
    agentChar = models.CharField(_("Agent"), max_length=140, blank=True, null=True)
    address = models.TextField(_("Address"), max_length=500,blank=True, null=True)
    pic = models.CharField(_("PIC"), max_length=140, blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=140, blank=True, null=True)
    weight = models.CharField(_("Weight"), max_length=140, blank=True, null=True)
    fax = models.CharField(_("Fax"), max_length=140, blank=True, null=True)
    dimensions = models.CharField(_("Dimensions"), max_length=140, blank=True, null=True)
    email = models.CharField(_("Email"), max_length=140, blank=True, null=True)
    
    dispatchDate = models.DateField(_("Dispatch Date"), default = timezone.now, blank = True)
    deliveryDate = models.DateField(_("Delivery Date"), default = timezone.now, blank = True)
    
    sellingTransportation = models.FloatField(_("Selling Transportation"), default = 0, blank = True, null = True)
    sellingTransportationCurrency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "selling_transportation_currency", default = 106, blank = True, null = True)
    sellingPacking = models.FloatField(_("Selling Packing"), default = 0, blank = True, null = True)
    sellingPackingCurrency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "selling_packing_currency", default = 106, blank = True, null = True)
    sellingInsurance = models.FloatField(_("Selling Insurance"), default = 0, blank = True, null = True)
    sellingInsuranceCurrency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "selling_insurance_currency", default = 106, blank = True, null = True)
    
    note = models.TextField(_("Note"), blank = True, null = True)
    
    #parts = models.ManyToManyField(PurchaseOrderPart,related_name='collections',through='CollectionPart', blank = True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.id)


class DispatchOrder(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="dispatch_order_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="dispatch_order_user")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    orderTracking = models.ForeignKey(OrderTracking, on_delete=models.CASCADE, blank = True, null = True)
    orderConfirmation = models.ForeignKey(OrderConfirmation, on_delete=models.CASCADE, blank = True, null = True)
    warehouse = models.ForeignKey("warehouse.Warehouse", on_delete=models.CASCADE, blank = True, null = True)

    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Order Confirmation Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Order Confirmation Code"), max_length=140, blank = True, null = True)
    dispatchOrderNo = models.CharField(_("Dispatch Order No"), max_length=140, blank = True, null=True, db_index = True)

    DISPATCH_STAGES = (
        ('dispatch_order_created', _('Dispatch Order Created')),
        ('picking', _('Picking')),
        ('loading', _('Loading')),
        ('transportation', _('Transportation')),
        ('delivery', _('Delivery')),
        ('finished', _('Finished')),
    )
    
    stage = models.CharField(_("Stage"), max_length=40, default="dispatch_order_created", choices = DISPATCH_STAGES)
    
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, blank = True, null=True)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, blank = True, null=True)
    address = models.TextField(_("Address"), max_length=500,blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=140, blank=True, null=True)
    email = models.CharField(_("Email"), max_length=140, blank=True, null=True)
    
    dispatchOrderDate = models.DateField(_("Dispatch Order Date"), default = timezone.now, blank = True)

    note = models.TextField(_("Note"), blank = True, null = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.id)
    
class DispatchOrderPart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="dispatch_order_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    dispatchOrder = models.ForeignKey(DispatchOrder, on_delete=models.CASCADE, blank = True, null = True)
    
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
    
    maker = models.ForeignKey(Maker, on_delete=models.DO_NOTHING, related_name = "dispatch_order_part_maker", blank = True, null = True)
    makerType = models.ForeignKey(MakerType, on_delete=models.DO_NOTHING, related_name = "dispatch_order_part_maker_type", blank = True, null = True)
    
    collectionPart = models.ForeignKey(CollectionPart, on_delete=models.CASCADE, related_name = "dispatch_order_part_part", blank = True)
    quantity = models.FloatField(_("Quantity"), default = 1, blank = True, null = True)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    note = models.TextField(_("Note"), max_length=1000, blank = True, null = True)
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        super(DispatchOrderPart, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.partNo)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['collectionPart', 'dispatchOrder'], name='unique_collectionPart_dispatchOrder')
        ]