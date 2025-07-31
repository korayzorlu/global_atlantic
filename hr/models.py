from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import translation
from django.utils.translation import gettext_lazy as _

# Create your models here.
from user.models import Currency


class TheCompany(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="the_company_source_company")
    name = models.CharField(_("Name"), max_length=255, blank=True)
    email = models.EmailField(_('email address'))
    url = models.URLField(_('url'))
    address = models.TextField(_("Address"), blank=True)
    address_2 = models.TextField(_("Address 2"), blank=True)
    tax_id = models.CharField(_("Tax ID"), max_length=50, blank=True)
    tax_office = models.CharField(_("Tax Office"), max_length=100, blank=True)
    kep_address = models.EmailField(blank=True)
    mersis_no = models.CharField(_("MERSIS No"), max_length=16, blank=True)
    phone_number = models.CharField(_("Phone Number"), max_length=50, blank=True, null=True)
    phone_number_2 = models.CharField(_("Phone Number 2"), max_length=50, blank=True, null=True)
    fax_number = models.CharField(_("Fax Number"), max_length=50, blank=True, null=True)
    fax_number_2 = models.CharField(_("Fax Number 2"), max_length=50, blank=True, null=True)
    legal_warning_text = models.TextField(_("Legal Warning"), blank=True)
    logo = models.ImageField(_("Logo"), upload_to='images/logo/', null=True)
   
    updated_by = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.id}:{self.name}'

    def clean(self):
        super().clean()
        if not self.id and TheCompany.objects.exists():
            raise ValidationError(_('You cannot add more companies.'))


class BankAccount(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="bank_account_source_company")
    TRANSACTION_TYPE_CHOICES = (
        ('IBAN', _('IBAN')),
        ('SWIFT', _('SWIFT')),
    )
    the_company = models.ForeignKey(TheCompany, on_delete=models.CASCADE, related_name="bank_accounts")
    name = models.CharField(_("Bank Name"), max_length=255, blank=True)
    translation_type= models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES, default='IBAN')
    currency = models.ForeignKey(Currency, on_delete=models.DO_NOTHING, blank=True, null=True)
    iban = models.CharField(_("IBAN"), max_length=34, blank=True, null=True)
    swift = models.CharField(_("Swift"), max_length=11, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = ('currency', 'iban',)

    def __str__(self):
        return f'{self.name}:{self.currency.name}'
    