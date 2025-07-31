import os

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
# Create your models here.
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model

from ckeditor.fields import RichTextField

from user.models import Team, Profile
from information.validators import ExtensionValidator
from card.models import Currency,Country,City
from data.models import Part
from account.models import IncomingInvoiceItem
from purchasing.models import PurchaseOrderItem
from sale.models import Project,Request

from django.utils import timezone

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="unknown")[0]

def part_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.id is None:
        return 'docs/{2}/data/part/temp/{0}/{1}'.format(instance.id, filename, instance.sourceCompany.id)
    else:
        return 'docs/{2}/data/part/{0}/{1}'.format(instance.id, filename, instance.sourceCompany.id)

class Warehouse(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="warehouse_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    
    code = models.CharField(_("Item Code"), max_length=140, blank = True, null = True)
    
    name = models.CharField(_("Name"), max_length=140, blank = True, null = True)
    
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name = "warehouse_country", blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.DO_NOTHING, related_name = "warehouse_city",)
    address = models.TextField(_("Address"), max_length = 150, blank=True, null=True)
    
    phone1 = models.CharField(_("Phone 1"), max_length=50, blank=True, null=True)
    phone2 = models.CharField(_("Phone 2"), max_length=50, blank=True, null=True)
    phone3 = models.CharField(_("Phone 2"), max_length=50, blank=True, null=True)
    phone4 = models.CharField(_("Phone 2"), max_length=50, blank=True, null=True)
    phone5 = models.CharField(_("Phone 2"), max_length=50, blank=True, null=True)
    
    fax = models.CharField(_("Fax 1"), max_length=50, blank=True, null=True)
    
    about = models.TextField(_("About"), blank = True, null = True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.code)

class ItemGroup(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="item_group_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name = "item_group_warehouse", blank = True, null = True)
    
    CATEGORIES = (
        ('part', _('Part')),
        ('asset', _('Asset')),
    )
    
    category = models.CharField(_("Category"), max_length=140, blank = True, null = True)
    
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
    name = models.CharField(_("Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "item_group_part", blank = True, null = True)

    barcode = models.CharField(_("Barcode"), max_length=140, blank = True, null = True)
    
    quantity = models.FloatField(_("Quantity"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), blank = True, null = True)
    
    image = models.ImageField(_("Logo"), blank = True, null = True, upload_to = part_directory_path)
    
    itemGroupDate = models.DateField(_("Item Date"), default = timezone.now, blank = True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.id is None:
            savedImage = self.image
            self.image = None
            super(ItemGroup, self).save(*args, **kwargs)
            self.image = savedImage
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        
        super(ItemGroup, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

class Item(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="item_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name = "item_warehouse", blank = True, null = True)
    
    itemGroup = models.ForeignKey(ItemGroup, on_delete=models.CASCADE, related_name = "item_item_group", blank = True, null = True)
    incomingInvoiceItem = models.ForeignKey(IncomingInvoiceItem, on_delete=models.SET_NULL, related_name = "item_incoming_invoice_item", blank = True, null = True)
    purchaseOrderItem = models.ForeignKey(PurchaseOrderItem, on_delete=models.SET_NULL, related_name = "item_purchase_order_item", blank = True, null = True)

    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "I", blank = True, null=True)
    dateCode = models.CharField(_("Date Code"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Item Code"), max_length=140, blank = True, null = True)
    itemNo = models.CharField(_("Item No"), max_length=140, blank = True, null=True, db_index = True)
    
    location = models.CharField(_("Location"), max_length=50, blank = True, null = True)
    
    CATEGORIES = (
        ('part', _('Part')),
        ('asset', _('Asset')),
    )
    
    category = models.CharField(_("Category"), max_length=140, blank = True, null = True)
    
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
    name = models.CharField(_("Name"), max_length=140, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "item_part", blank = True, null = True)

    barcode = models.CharField(_("Barcode"), max_length=140, blank = True, null = True)
    
    currency = models.ForeignKey(Currency, related_name = "item_currency", on_delete=models.SET_DEFAULT, default = 106)
    buyingPrice = models.FloatField(_("Buying Prince"), default = 0.00, blank = True, null = True)
    cost = models.FloatField(_("Cost"), default = 0.00, blank = True, null = True)
    salePrice = models.FloatField(_("Sale Price"), default = 0.00, blank = True, null = True)
    vat = models.FloatField(_("Vat"), default = 0, blank = True, null = True)
    
    weight = models.FloatField(_("Weight"), default = 0, blank = True, null = True)
    width = models.FloatField(_("Weight"), default = 0, blank = True, null = True)
    height = models.FloatField(_("Weight"), default = 0, blank = True, null = True)
    
    quantity = models.FloatField(_("Quantity"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), blank = True, null = True)
    
    image = models.ImageField(_("Logo"), blank = True, null = True, upload_to = part_directory_path)
    
    itemDate = models.DateField(_("Item Date"), default = timezone.now, blank = True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.id is None:
            savedImage = self.image
            self.image = None
            super(Item, self).save(*args, **kwargs)
            self.image = savedImage
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.itemNo)
    
class Dispatch(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="dispatch_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="dispatch_user")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null = True, blank = True,related_name="dispatch_project")
    theRequest = models.ForeignKey(Request, on_delete=models.CASCADE, null = True, blank = True,related_name="dispatch_request")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)

    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Dispatch  Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Dispatch  Code"), max_length=140, blank = True, null = True)
    dispatchNo = models.CharField(_("Dispatch  No"), max_length=140, blank = True, null=True, db_index = True)
    
    dispatchDate = models.DateField(_("Dispatch  Date"), default = timezone.now, blank = True)
    
    note = models.TextField(_("Note"), max_length = 500, blank = True, null = True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.dispatchNo)

    class Meta:
        ordering = ['dispatchDate']