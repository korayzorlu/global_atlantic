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

from django_filters import FilterSet, ChoiceFilter

from card.models import Company, Person, Currency
from data.models import Part,Expense,ServiceCard

from decimal import Decimal, ROUND_UP

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="unknown")[0]

def purchase_order_document_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    return 'docs/{2}/purchasing/purchase_order/documents/{0}/{1}'.format(instance.purchaseOrder.purchaseOrderNo, filename,instance.sourceCompany.id)
    
class Project(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="purchasing_project_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="project_user")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Project Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Project Code"), max_length=140, blank = True, null = True)
    projectNo = models.CharField(_("Project No"), max_length=140, blank = True, null=True, db_index = True)
    
    PROJECT_STAGES = (
        ('project', _('Project')),
        ('inquiry', _('Inquiry')),
        ('purchase_order', _('Purchase Order')),
        ('invoiced', _('Invoiced')),
        ('warehouse', _('Warehouse')),
    )
    
    stage = models.CharField(_("Stage"), max_length=40, default="project", blank= True, null=True, choices = PROJECT_STAGES)
    
    invoiced = models.BooleanField(_("Invoiced"), default = False)
    
    supplier = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank = True, null=True)
    supplierRef = models.CharField(_("Supplier Ref"), max_length=140, blank = True, null=True)
    customerRef = models.CharField(_("Customer Ref"), max_length=140, blank = True, null=True)
    
    projectDate = models.DateField(_("Project Date"), default = timezone.now, blank = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.projectNo)

    class Meta:
        ordering = ['projectDate']

class ProjectItem(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="project_item_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank = True, null = True)
    
    trDescription = models.TextField(_("Turkish Description"), max_length=250, null=True, blank = True)

    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "project_part", blank = True, null = True)
    serviceCard = models.ForeignKey(ServiceCard, on_delete=models.CASCADE, related_name = "project_service_card", blank = True, null = True)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name = "project_expense", blank = True, null = True)
    
    name = models.CharField(_("Name"), max_length=140, blank = True, null = True)
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
    
    startDate = models.DateField(_("Send Invoice Date"), default = timezone.now, null = True, blank = True)
    endDate = models.DateField(_("Payment Date"), default = timezone.now, null = True, blank = True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def save(self, *args, **kwargs):
        
        super(ProjectItem, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)
    
class Inquiry(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="purchasing_inquiry_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="purchasing_inquiry_user")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank = True, null = True, related_name="purhasing_inquiry_project")
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Inquiry Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Inquiry Code"), max_length=140, blank = True, null = True)
    inquiryNo = models.CharField(_("Inquiry No"), max_length=140, blank = True, null=True, db_index = True)
    
    APPROVES = (
        ('notSent', _('Not Sent For Approval')),
        ('sent', _('Sent For Approval')),
        ('approved', _('Approved By Manager')),
        ('notApproved', _('Not Approved By Manager')),
    )
    
    approval = models.CharField(max_length=30, choices=APPROVES, default = "notSent", blank = True, null = True)
    
    supplier = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="purchasing_inquiry_supplier")
    
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank = True, null=True, related_name="purchasing_inquiry_uperson")
    supplierRef = models.CharField(_("Supplier Ref"), max_length=140, blank = True, null=True)
    payment = models.CharField(_("Payment"), max_length=140, blank = True, null=True)
    
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "inquiry_item_currency", default = 106, blank = True, null = True)
    
    note = models.TextField(_("Note"), max_length = 500, blank = True, null = True)
    
    totalTotalPrice = models.FloatField(_("Total Total Prince"), default = 0, blank = True, null = True)
    
    inquiryDate = models.DateField(_("Inquiry Date"), default = timezone.now, blank = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.inquiryNo)

    class Meta:
        ordering = ['inquiryDate']
 
class InquiryItem(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="inquiry_item_source_company")
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
    
    projectItem = models.ForeignKey(ProjectItem, on_delete=models.CASCADE, related_name = "inquiry_item_item", blank = True)
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
    
    name = models.CharField(_("Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    unit = models.CharField(_("Units"), default = "pc", max_length=40, choices = UNITS)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Prince"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Prince"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), max_length=1000, blank = True, null = True)
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)
    
    def save(self, *args, **kwargs):
        
        #self.totalPrice = float(self.unitPrice) * int(self.quantity)
        
        super(InquiryItem, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.projectItem.name)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['projectItem', 'inquiry'], name='unique_projectItem_inquiry')
        ]
        
class PurchaseOrder(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="purchasing_purchase_order_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="purchasing_purchase_order_user")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank = True,related_name="purchasing_purchase_order")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, blank = True, null = True, related_name="purchasing_purchase_order_inquiry")
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Purchase Order Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Purchase Order Code"), max_length=140, blank = True, null = True)
    purchaseOrderNo = models.CharField(_("Purchase Order No"), max_length=140, blank = True, null=True, db_index = True)
    
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, related_name = "purchasing_purchase_order_currency", default = 106, blank = True, null = True)

    payment = models.CharField(max_length=30, blank = True, null = True)
    delivery = models.CharField(_("Delivery"), max_length=140, blank = True, null = True)

    customsDuty = models.FloatField(_("Customs Duty"), default = 0, blank = True, null = True)
    additionalCustomsDuty = models.FloatField(_("Additional Customs Duty"), default = 0, blank = True, null = True)
    stampDuty = models.FloatField(_("Stamp Duty"), default = 0, blank = True, null = True)

    discount = models.FloatField(_("Discount"), default = 0, blank = True, null = True)
    discountAmount = models.FloatField(_("Discount Amount"), default = 0, blank = True, null = True)
    
    totalDiscountPrice = models.FloatField(_("Total Discount Prince"), default = 0, blank = True, null = True)
    totalTotalPrice = models.FloatField(_("Total Prince"), default = 0, blank = True, null = True)
    
    rate = models.CharField(_("Rate"), max_length=140, blank = True, null = True)
    
    invoiced = models.BooleanField(_("Invoiced"), default = False)
    incomingInvoiced = models.BooleanField(_("Incoming Invoiced"), default = False)
    
    orderDueDate = models.DateField(_("Order Due Date"), default = timezone.now, blank = True)
    
    purchaseOrderDate = models.DateField(_("Purchase Order Date"), default = timezone.now, blank = True)
    
    note = models.TextField(_("Note"), max_length = 500, blank = True, null = True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.purchaseOrderNo)

    class Meta:
        ordering = ['purchaseOrderDate']
       
class PurchaseOrderItem(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="purchasing_purchase_order_part_source_company")
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
    
    name = models.CharField(_("Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    unit = models.CharField(_("Units"), default = "pc", max_length=40, choices = UNITS)
    
    AVAILABILITIES = (
        ('day', _('Day')),
        ('week', _('Week')),
        ('tba', _('TBA')),
        ('ex_stock', _('Ex Stock')),
        ('ex_stock_istanbul', _('Ex Stock Istanbul')),
    )
    
    availabilityType = models.CharField(max_length=30, choices=AVAILABILITIES, default='day', blank=True, null=True)
    availability = models.IntegerField(_("Availability"), blank=True, null=True)
    
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
    
    inquiryItem = models.ForeignKey(InquiryItem, on_delete=models.CASCADE, related_name = "purchasing_purchaseOrder_item_item", blank = True)
    quantity = models.FloatField(_("Quantity"), default = 1, blank = True, null = True)
    
    sequency = models.IntegerField(_("Sequency"), default=1, blank = True, null = True)
    
    unitPrice = models.FloatField(_("Unit Prince"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Prince"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), max_length=1000, blank = True, null = True)
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)

    placedItems = models.FloatField(_("Placed Items"), default = 0, blank = True, null = True)
    placed = models.BooleanField(_("Placed"), default = False)
    
    def save(self, *args, **kwargs):
        self.totalPrice = float(self.unitPrice) * float(self.quantity)
        
        super(PurchaseOrderItem, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['inquiryItem', 'purchaseOrder'], name='unique_inquiryItem_purchaseOrder')
        ]

class PurchaseOrderDocument(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="purchase_order_document_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    purchaseOrder = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, blank = True, null = True)
    
    file = models.FileField(_("File"), blank =True, null = True, upload_to = purchase_order_document_directory_path)
    name = models.CharField(_("File Name"), max_length=140, blank = True, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        
        if self.file:
            self.name = os.path.basename(self.file.name)
        
        super(PurchaseOrderDocument, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)