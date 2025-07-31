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
from card.models import Currency


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="unknown")[0]

def part_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.id is None:
        return 'docs/{2}/data/part/temp/{0}/{1}'.format(instance.id, filename, instance.sourceCompany.id)
    else:
        return 'docs/{2}/data/part/{0}/{1}'.format(instance.id, filename, instance.sourceCompany.id)
    
def part_set_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.id is None:
        return 'docs/{2}/data/part_set/temp/{0}/{1}'.format(instance.id, filename, instance.sourceCompany.id)
    else:
        return 'docs/{2}/data/part_set/{0}/{1}'.format(instance.id, filename, instance.sourceCompany.id)

def part_image_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.id is None:
        return 'docs/{2}/data/part/temp/{0}/{1}'.format(instance.part.partNo, filename, instance.sourceCompany.id)
    else:
        return 'docs/{2}/data/part/{0}/{1}'.format(instance.part.partNo, filename, instance.sourceCompany.id)

class UniqueAutoIncrementField(models.Field):
    def __init__(self, start_value=100, *args, **kwargs):
        self.start_value = start_value
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if add and not getattr(model_instance, self.attname):
            # Yeni bir nesne oluşturuluyor ve alan değeri henüz belirlenmemişse
            last_object = model_instance.__class__.objects.order_by('-code').first()
            if last_object:
                # En son oluşturulan nesnenin id'sini al
                last_id = last_object.code
            else:
                # Veritabanında hiç nesne yoksa, start_value değerini kullan
                last_id = self.start_value - 1

            # Yeni nesnenin alan değerini bir sonraki sayı olarak ayarla
            setattr(model_instance, self.attname, last_id + 1)

        return super().pre_save(model_instance, add)

    def db_type(self, connection):
        return 'integer'
    
class UniqueAutoIncrementFieldPart(models.Field):
    def __init__(self, start_value=1, *args, part_unique=1, **kwargs):
        self.start_value = start_value
        self.partUnique = part_unique
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if add and not getattr(model_instance, self.attname):
            # Yeni bir nesne oluşturuluyor ve alan değeri henüz belirlenmemişse
            last_object = model_instance.__class__.objects.filter(partUnique = self.partUnique).order_by('-code').first()
            if last_object:
                # En son oluşturulan nesnenin id'sini al
                last_id = last_object.partUniqueCode
            else:
                # Veritabanında hiç nesne yoksa, start_value değerini kullan
                last_id = self.start_value - 1

            # Yeni nesnenin alan değerini bir sonraki sayı olarak ayarla
            setattr(model_instance, self.attname, last_id + 1)

        return super().pre_save(model_instance, add)

    def db_type(self, connection):
        return 'integer'

class Maker(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="maker_source_company")
    name = models.CharField(_("Maker Name"), max_length=140)
    info = models.TextField(_("Info"), blank = True, null = True)
    
    type = models.JSONField(_("Type"),blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

class MakerType(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="maker_type_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.DO_NOTHING, null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    maker = models.ForeignKey(Maker, on_delete=models.CASCADE, related_name="maker_type_maker", blank = True, null = True)
    name = models.CharField(_("Maker Type Name"), max_length=140, blank = True, null = True)
    type = models.CharField(_("Type"), max_length=140)
    note = models.CharField(_("Note"), max_length=140, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.type)

class PartUnique(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="part_unique_source_company")
    code = UniqueAutoIncrementField(start_value = 100, unique = False)
    description = models.CharField(_("Description"), max_length=140,blank = True, null = True)

    def __str__(self):
        return str(self.code)

class Part(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    partUnique = models.ForeignKey(PartUnique, on_delete=models.CASCADE, related_name="part_unique", blank = True, null = True)
    partUniqueCode = models.IntegerField(_("Part Unique Code"), blank = True, null = True)
    
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
    
    group = models.CharField(_("Group"), max_length=140, blank = True, null = True)
    unit = models.CharField(_("Units"), default = "pc", max_length=40, choices = UNITS)
    description = models.TextField(_("Description"), max_length=250, blank = True, db_index = True)
    partNo = models.CharField(_("Part No"), max_length=140, null=True, blank = True, db_index = True)
    maker = models.ForeignKey(Maker, on_delete=models.CASCADE, related_name="part_maker", null = True, blank = True)
    type = models.ForeignKey(MakerType, on_delete=models.CASCADE, related_name="part_maker_type", blank = True, null = True)
    manufacturer = models.CharField(_("Manufacturer"), max_length=140, blank = True, null = True)
    
    drawingNr = models.CharField(_("Drawing Nr"), max_length=140, blank = True, null = True)
    techncialSpecification = models.CharField(_("Techncial Specification"), max_length=140, blank = True, null = True)
    consumable = models.BooleanField(_("Consumable"), default = True)
    
    crossRef = models.CharField(_("Cross Ref"), max_length=140, blank = True, null = True)
    ourRef = models.CharField(_("Our Ref"), max_length=140, blank = True, null = True)
    barcode = models.CharField(_("Barcode"), max_length=140, blank = True, null = True)

    hsCode = models.CharField(_("HS Code"), max_length=140, blank = True, null = True)
    
    currency = models.ForeignKey(Currency, related_name = "curency_for_part", on_delete=models.SET_DEFAULT, default = 106)
    buyingPrice = models.FloatField(_("Buying Prince"), default = 0.00, blank = True, null = True)
    retailPrice = models.FloatField(_("Retail Price"), default = 0.00, blank = True, null = True)
    dealerPrice = models.FloatField(_("Dealer Price"), default = 0.00, blank = True, null = True)
    wholesalePrice = models.FloatField(_("Wholesale Price"), default = 0.00, blank = True, null = True)
    
    weight = models.CharField(_("Weight"), max_length=140, blank = True, null = True)
    
    quantity = models.FloatField(_("Quantity"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), blank = True, null = True)
    
    image = models.ImageField(_("Logo"), blank = True, null = True, upload_to = part_directory_path)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.id is None:
            savedImage = self.image
            self.image = None
            super(Part, self).save(*args, **kwargs)
            self.image = savedImage
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        
        super(Part, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.partNo)

class PartImage(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="part_image_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    part = models.ForeignKey(Part, on_delete=models.CASCADE, blank = True, null = True)
    
    image = models.ImageField(_("Image"), blank =True, null = True, upload_to = part_image_directory_path)
    
    def __str__(self):
        return str(self.part.partNo)

 
# class PartSet(models.Model):
#     name = models.CharField(_("Name"), max_length=140, blank = True, null = True)
#     group = models.CharField(_("Group"), max_length=140, blank = True, null = True)
    
#     UNITS = (
#         ('ad', _('ad')),
#         ('koli', _('koli')),
#         ('mm', _('MM')),
#         ('pc', _('PC')),
#         ('pcs', _('PCS')),
#         ('pk', _('PK')),
#     )
    
#     group = models.CharField(_("Group"), max_length=140, blank = True, null = True)
#     unit = models.CharField(_("Units"), default = "pc", max_length=40, choices = UNITS)
#     description = models.TextField(_("Part Set Description"), null=True, blank = True)
#     maker = models.ForeignKey(Maker, on_delete=models.CASCADE, related_name="part_maker", blank = True)
#     type = models.ForeignKey(MakerType, on_delete=models.CASCADE, related_name="part_maker_type", blank = True, null = True)
#     manufacturer = models.CharField(_("Manufacturer"), max_length=140, blank = True, null = True)
    
#     customizeQuantity = models.BooleanField(_("Customize Quantity"), default = False)
    
#     crossRef = models.CharField(_("Cross Ref"), max_length=140, blank = True, null = True)
#     ourRef = models.CharField(_("Our Ref"), max_length=140, blank = True, null = True)
#     barcode = models.CharField(_("Barcode"), max_length=140, blank = True, null = True)
    
#     currency = models.ForeignKey(Currency, related_name = "curency_for_part", on_delete=models.SET_DEFAULT, default = 106)
#     buyingPrice = models.FloatField(_("Buying Prince"), default = 0.00, blank = True, null = True)
#     retailPrice = models.FloatField(_("Retail Price"), default = 0.00, blank = True, null = True)
#     dealerPrice = models.FloatField(_("Dealer Price"), default = 0.00, blank = True, null = True)
#     wholesalePrice = models.FloatField(_("Wholesale Price"), default = 0.00, blank = True, null = True)
    
#     quantity = models.FloatField(_("Quantity"), default = 0, blank = True, null = True)
    
#     note = models.TextField(_("Note"), blank = True, null = True)
    
#     image = models.ImageField(_("Image"), blank = True, null = True, upload_to = part_set_directory_path)

#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True, null=True)

#     def __str__(self):
#         return str(self.name)    
    

class ServiceCard(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="service_card_source_company")
    MACHINE_TYPES = (
        ('2-zamanli', _('2 Zamanlı')),
        ('4-zamanli', _('4 Zamanlı')),
        ('genel', _('Genel')),
    )
    machineType = models.CharField(_("Machine Types"), max_length=40, blank = True, null = True, choices = MACHINE_TYPES)
    name = models.CharField(_("Service Name"), max_length=140)
    code = models.CharField(_("Service Code"), max_length=140)
    group = models.CharField(_("Service Group"), max_length=140, blank = True, null = True)
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
    quantity = models.FloatField(_("Quantity"), default = 0.00, blank = True, null = True)
    about = models.TextField(_("about"), blank = True, null = True)
    
    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']


    
class Expense(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="expense_source_company")
    name = models.CharField(_("Expense Name"), max_length=140)
    code = models.CharField(_("Expense Code"), max_length=140)
    group = models.CharField(_("Expense Group"), max_length=140, blank = True, null = True)
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
    quantity = models.FloatField(_("Quantity"), default = 0.00, blank = True, null = True)
    description = models.TextField(_("Description"), max_length=500, blank = True, null = True)
    
    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

class Excel(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="data_source_company")
    file = models.FileField(blank =True, null = True, verbose_name = "Excel File")