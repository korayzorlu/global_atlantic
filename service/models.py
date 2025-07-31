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

from card.models import Company, Vessel, Person, Currency, Country, EnginePart
from data.models import Maker, MakerType, Part, ServiceCard, Expense

from decimal import Decimal, ROUND_UP

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="unknown")[0]

def offer_image_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.id is None:
        return 'docs/{2}/service/offer/temp/{0}/{1}'.format(instance.offer.offerNo, filename, instance.sourceCompany.id)
    else:
        return 'docs/{2}/service/offer/{0}/{1}'.format(instance.offer.offerNo, filename, instance.sourceCompany.id)
    
def offer_document_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    return 'docs/{2}/service/offer/documents/{0}/{1}'.format(instance.offer.offerNo, filename,instance.sourceCompany.id)

class Acceptance(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="acceptance_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null=True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "ESM", blank = True, null=True)
    yearCode = models.CharField(_("Offer Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Offer Code"), max_length=140, blank = True, null = True)
    acceptanceNo = models.CharField(_("Offer No"), max_length=140, blank = True, null=True)
    
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank = True)
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank = True, null = True)
    vessel = models.ForeignKey(Vessel, on_delete=models.DO_NOTHING, blank = True, null = True)
    equipment = models.ForeignKey(EnginePart, on_delete=models.DO_NOTHING, blank = True, null = True)
    customerRef = models.CharField(_("Customer Ref"), max_length=140, blank = True, null=True)
    paymentType = models.CharField(_("Payment Type"), max_length=140, blank = True, null=True)
    deliveryMethod = models.CharField(_("Delivery Method"), max_length=140, blank = True, null=True)
    
    MACHINE_TYPES = (
        ('2-zamanli', _('2 Zamanlı')),
        ('4-zamanli', _('4 Zamanlı')),
        ('genel', _('Genel')),
    )
    machineType = models.CharField(_("Machine Types"), max_length=40, blank = True, null = True, choices = MACHINE_TYPES)
    
    acceptanceDate = models.DateField(_("Offer Date"), default = timezone.now, blank = True)
    
    period = models.CharField(_("Period"), max_length=140, blank = True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.DO_NOTHING, blank = True, null = True)
    discount = models.FloatField(_("Discount"), default = 0, blank = True, null = True)
    discountAmount = models.FloatField(_("Discount Amount"), default = 0, blank = True, null = True)
    
    totalDiscountPrice = models.FloatField(_("Total Discount Price"), default = 0, blank = True, null = True)
    totalTotalPrice = models.FloatField(_("Total Total Price"), default = 0, blank = True, null = True)
    
    STATUS_CHOICES = (
        ('accepted', _('Accepted')),
        ('cancelled', _('Cancelled')),
        ('active', _('Active')),
        ('finished', _('Finished')),
    )
    status = models.CharField(_("Status"), max_length=40, blank = True, choices = STATUS_CHOICES, default = "accepted")
    
    note = models.TextField(_("Note"), max_length = 500, blank = True, null = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.acceptanceNo)

    class Meta:
        ordering = ['-acceptanceDate']

class AcceptanceEquipment(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="acceptance_equipment_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    acceptance = models.ForeignKey(Acceptance, on_delete=models.CASCADE, blank = True, null = True)
    
    equipment = models.ForeignKey(EnginePart, on_delete=models.CASCADE, blank = True, null = True)
    
    def __str__(self):
        return str(self.equipment.serialNo)

class AcceptanceServiceCard(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="acceptance_service_card_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    acceptance = models.ForeignKey(Acceptance, on_delete=models.CASCADE, blank = True, null = True)
    
    serviceCard = models.ForeignKey(ServiceCard, on_delete=models.CASCADE, related_name = "acceptance_service_card_service_card")
    quantity = models.FloatField(default=1)
    unitPrice1 = models.FloatField(_("Unit Prince 3"), default = 0, blank = True, null = True)
    unitPrice2 = models.FloatField(_("Unit Prince 2"), default = 0, blank = True, null = True)
    unitPrice3 = models.FloatField(_("Unit Prince 3"), default = 0, blank = True, null = True)
    profit = models.FloatField(_("Profit"), default = 0, blank = True, null = True)
    discount = models.FloatField(_("Discount"), default = 0, blank = True, null = True)
    tax = models.FloatField(_("Tax"), default = 0, blank = True, null = True)
    taxPrice = models.FloatField(_("Tax Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), max_length=1000, blank = True, null = True)
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)
    
    extra = models.BooleanField(_("Extra"), default = False)
    
    def __str__(self):
        return str(self.serviceCard.code)


class AcceptancePart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="acceptance_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    acceptance = models.ForeignKey(Acceptance, on_delete=models.CASCADE, blank = True, null = True)
    
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "acceptance_part_part")
    quantity = models.FloatField(default=1)
    unitPrice = models.FloatField(_("Unit Prince"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    extra = models.BooleanField(_("Extra"), default = False)
    
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)
    
    def __str__(self):
        return str(self.part.partNo)



class Offer(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="offer_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null=True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    
    identificationCode = models.CharField(_("Identification Code"), max_length=140, default = "", blank = True, null=True)
    yearCode = models.CharField(_("Offer Year"), max_length=140, blank = True, null = True)
    code = models.CharField(_("Offer Code"), max_length=140, blank = True, null = True)
    offerNo = models.CharField(_("Offer No"), max_length=140, blank = True, null=True)
    
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank = True)
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING, blank = True, null = True)
    vessel = models.ForeignKey(Vessel, on_delete=models.DO_NOTHING, blank = True, null = True)
    equipment = models.ForeignKey(EnginePart, on_delete=models.DO_NOTHING, blank = True, null = True)
    customerRef = models.CharField(_("Customer Ref"), max_length=140, blank = True, null=True)
    paymentType = models.CharField(_("Payment Type"), max_length=140, blank = True, null=True)
    deliveryMethod = models.CharField(_("Delivery Method"), max_length=140, blank = True, null=True)
    
    note = models.TextField(_("Note"), max_length = 500, default = "", blank = True, null = True)
    
    MACHINE_TYPES = (
        ('2-zamanli', _('2 Zamanlı')),
        ('4-zamanli', _('4 Zamanlı')),
        ('genel', _('Genel')),
    )
    machineType = models.CharField(_("Machine Types"), max_length=40, blank = True, null = True, choices = MACHINE_TYPES)
    
    offerDate = models.DateField(_("Offer Date"), default = timezone.now, blank = True)
    
    period = models.CharField(_("Period"), max_length=140, blank = True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.DO_NOTHING,default = 106, blank = True, null = True)
    discount = models.FloatField(_("Discount"), default = 0, blank = True, null = True)
    discountAmount = models.FloatField(_("Discount Amount"), default = 0, blank = True, null = True)
    
    totalDiscountPrice = models.FloatField(_("Total Discount Price"), default = 0, blank = True, null = True)
    totalTotalPrice = models.FloatField(_("Total Total Price"), default = 0, blank = True, null = True)
    
    confirmed = models.BooleanField(_("Confirmed"), default = False)
    finished = models.BooleanField(_("Finished"), default = False)
    invoiced = models.BooleanField(_("Invoiced"), default = False)
    sendInvoiced = models.BooleanField(_("Send Invoiced"), default = False)
    
    STATUS_CHOICES = (
        ('offer', _('Offer')),
        ('active', _('Active')),
        ('finished', _('Finished')),
    )
    status = models.CharField(_("Status"), max_length=40, blank = True, choices = STATUS_CHOICES, default = "offer")
    
    note = models.TextField(_("Note"), max_length = 500, blank = True, null = True)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return str(self.offerNo)

    class Meta:
        ordering = ['offerDate']
        
class OfferServiceCard(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="offer_service_card_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, blank = True, null = True)
    
    serviceCard = models.ForeignKey(ServiceCard, on_delete=models.CASCADE, related_name = "offer_service_card_service_card")
    quantity = models.FloatField(default=1)
    unitPrice1 = models.FloatField(_("Unit Prince 3"), default = 0, blank = True, null = True)
    unitPrice2 = models.FloatField(_("Unit Prince 2"), default = 0, blank = True, null = True)
    unitPrice3 = models.FloatField(_("Unit Prince 3"), default = 0, blank = True, null = True)
    profit = models.FloatField(_("Profit"), default = 0, blank = True, null = True)
    discount = models.FloatField(_("Discount"), default = 0, blank = True, null = True)
    tax = models.FloatField(_("Tax"), default = 0, blank = True, null = True)
    taxPrice = models.FloatField(_("Tax Price"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    note = models.TextField(_("Note"), max_length=1000, blank = True, null = True)
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)
    
    extra = models.BooleanField(_("Extra"), default = False)
    
    def __str__(self):
        return str(self.serviceCard.code)
        
class OfferExpense(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="offer_expense_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, blank = True, null = True)
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name = "offer_expense_expense")
    quantity = models.FloatField(default=1)
    unitPrice = models.FloatField(_("Unit Prince"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    extra = models.BooleanField(_("Extra"), default = False)
    
    def __str__(self):
        return str(self.expense.code)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['expense', 'offer'], name='unique_expense_offer')
        ]
        

class OfferPart(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="offer_part_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, blank = True, null = True)
    
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name = "offer_part_part")
    quantity = models.FloatField(default=1)
    unitPrice = models.FloatField(_("Unit Prince"), default = 0, blank = True, null = True)
    totalPrice = models.FloatField(_("Total Price"), default = 0, blank = True, null = True)
    
    extra = models.BooleanField(_("Extra"), default = False)
    
    remark = models.TextField(_("Remark"), max_length=1000, blank = True, null = True)
    
    def __str__(self):
        return str(self.part.partNo)


        
class OfferImage(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="offer_image_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, blank = True, null = True)
    
    image = models.ImageField(_("Image"), blank =True, null = True, upload_to = offer_image_directory_path)
    
    def __str__(self):
        return str(self.offer.offerNo)

class OfferDocument(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="offer_document_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user),null = True, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, blank = True, null = True)
    
    file = models.FileField(_("File"), blank =True, null = True, upload_to = offer_document_directory_path)
    name = models.CharField(_("File Name"), max_length=140, blank = True, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        
        if self.file:
            self.name = os.path.basename(self.file.name)
        
        super(OfferDocument, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)

class OfferNote(models.Model):
    """
    Stores the note
    """
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="offer_note_source_company")
    user = models.ForeignKey("auth.User", on_delete=models.DO_NOTHING, blank = True)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, blank = True, null = True)
    
    title = models.CharField(_("Title"), max_length=50, blank = True, null = True)
    text = models.TextField(_("Text"), max_length=500, blank = True, null = True)
    offerNoteDate = models.DateField(_("Offer Date"), default = timezone.now, blank = True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ['-created_date']

# class ActiveProject(models.Model):
#     user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null=True)
#     sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
#     offer = models.ForeignKey(Offer, on_delete=models.CASCADE, blank = True, null = True, related_name="active_project_offer")

#     created_date = models.DateTimeField(auto_now_add=True, null=True)
#     updated_date = models.DateTimeField(auto_now=True, null=True)
    
#     def __str__(self):
#         return str(self.offer.offerNo)

#     class Meta:
#         ordering = ['created_date']