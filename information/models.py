import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
# Create your models here.
from simple_history.models import HistoricalRecords

from user.models import Team
from information.validators import ExtensionValidator


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


class CompanyGroup(models.Model):
    name = models.CharField(_("Company Group Name"), max_length=140, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    company_type_choices = (
        ('Customer', _('Customer')),
        ('Supplier', _('Supplier')),
        ('Customer & Supplier', _('Customer & Supplier')),
    )
    name = models.CharField(_("Company Name"), max_length=140)
    company_group = models.ForeignKey(CompanyGroup, verbose_name=_('Company Group'), max_length=140, blank=True,
                                      null=True, on_delete=models.SET_NULL, related_name="companies")
    company_type = models.CharField(_("Company Type"), max_length=40, default="Customer", choices=company_type_choices)

    direct_phone = models.CharField(_("Direct Phone"), max_length=50)
    phone1 = models.CharField(_("Phone 1"), max_length=50, blank=True, null=True)
    phone2 = models.CharField(_("Phone 2"), max_length=50, blank=True, null=True)
    fax_address = models.CharField(_("Fax Address"), max_length=50, blank=True, null=True)
    email = models.EmailField()

    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.DO_NOTHING)

    sales_team = models.ForeignKey(Team, verbose_name=_('Sales Team'), null=True, on_delete=models.SET_NULL)
    customer_representative = models.ForeignKey(User, verbose_name=_('Customer Representative'), null=True,
                                                on_delete=models.SET_NULL)
    key_account = models.ForeignKey(User, related_name="key_accounts", verbose_name=_('Key Account'), null=True,
                                    on_delete=models.SET_NULL)

    vat_office = models.CharField(_("Vat Office"), max_length=100, blank=True, null=True)
    vat_no = models.CharField(_("Vat No"), max_length=50, blank=True, null=True)

    website = models.URLField(max_length=100, blank=True, null=True)
    address = models.TextField(_("Address"))

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

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

    def is_customer(self):
        return self.company_type in ['Customer', 'Customer & Supplier']


class Contact(models.Model):
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'))
    birthday = models.DateField(_("Birthday"), blank=True, null=True)
    phone_number = models.CharField(_("Phone Number"), max_length=50)
    company = models.ManyToManyField(Company, related_name="contacts")
    default_person_in_contact_of = models.OneToOneField(Company, on_delete=models.SET_NULL, null=True, blank=True,
                                                        related_name="default_person_in_contact")
    office_address = models.TextField(_("Office Address"))
    position = models.CharField(_("Position"), max_length=140)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.get_full_name()

    class Meta:
        ordering = ['id']

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

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


class ContactCompanyHistory(models.Model):
    WORKING_STATUS_CHOICES = (
        ('working', _('Working')),
        ('not_working', _('Not Working')),
    )
    company = models.ForeignKey(Company, related_name="contact_history", on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, related_name="company_history", on_delete=models.CASCADE)
    working_status = models.CharField(choices=WORKING_STATUS_CHOICES, max_length=20, default='working')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.company.name} -> {self.contact.get_full_name()} | {self.get_working_status_display()}"

    class Meta:
        unique_together = ['company', 'contact']
        ordering = ['-working_status']


class Vessel(models.Model):
    """
    Vessel information are kept in this table
    """
    STATUS_CHOICES = (
        ('available', _('Available')),
        ('not_available', _('Not Available')),
    )
    TYPE_CHOICES = (
        ('M/V', _('(M/V) Motor, Vessel'),),
        ('M/T', _('(M/T) Motor, Tanker'),),
        ('M/F', _('(M/F) Motor, Ferry')),
        ('M/Y', _('(M/Y) Motor, Yatch'),),
        ('M/TUG', _('(M/TUG) Motor, Tug'),),
        ('NB', _('(NB) Undefined')),
    )
    manager_company = models.ForeignKey(CompanyGroup, on_delete=models.SET_NULL, blank=True, null=True)
    owner_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name="vessels",
                                      limit_choices_to=Q(company_type__contains="Customer"))
    name = models.CharField(_("Vessel Name"), max_length=100, unique=True)
    person_in_contacts = models.ManyToManyField(Contact, limit_choices_to=Q(company__company_type__contains="Customer"))
    type = models.CharField(_("Vessel Type"), default="M/V", choices=TYPE_CHOICES, max_length=10)
    imo = models.CharField(_("IMO Number"), max_length=7, null=True)
    flag = models.ImageField(_("Flag"), upload_to='images/flags/')
    flag_name = models.CharField(_("Flag Name"), max_length=40, null=True)
    gross_ton = models.IntegerField(_("Gross Ton"), blank=True, null=True)
    deadweight = models.IntegerField(_("Deadweight"), blank=True, null=True)
    year_built = models.IntegerField(_("Year Built"), blank=True, null=True)
    hull_no = models.CharField(_("Hull No"), max_length=20, blank=True, null=True)
    shipyard = models.CharField(_("Shipyard"), max_length=60, blank=True, null=True)
    status = models.CharField(_("Status"), choices=STATUS_CHOICES, default="available", max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

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

    def all_changes(self):
        verbose_names_of_choices = dict((x, y) for x, y in (self.STATUS_CHOICES + self.TYPE_CHOICES))
        changes = []
        recent = None
        for history in self.history.all():
            if recent:
                delta = recent.diff_against(history)
                for change in delta.changes:
                    data = {'field': self._meta.get_field(change.field).verbose_name.title()}
                    if self._meta.get_field(change.field).__class__.__name__ == "BooleanField":
                        data["old"] = True if change.old else "False"
                        data["new"] = True if change.new else "False"
                    elif self._meta.get_field(change.field).choices:
                        data["old"] = verbose_names_of_choices[change.old]
                        data["new"] = verbose_names_of_choices[change.new]
                    elif self._meta.get_field(change.field).__class__.__name__ == "ForeignKey":
                        old_obj = self._meta.get_field(change.field).remote_field.model.objects.filter(pk=change.old)
                        data["old"] = old_obj[0] if old_obj else None
                        new_obj = self._meta.get_field(change.field).remote_field.model.objects.filter(pk=change.new)
                        data["new"] = new_obj[0] if new_obj else None
                    else:
                        data["old"] = change.old
                        data["new"] = change.new
                    data["date"] = recent.history_date
                    changes.append(data)
            recent = history
        return changes
    

# class VesselChangeHistory(models.Model):
#     """
#     Vessel Change History information are kept in this table
#     """
#     vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, null=True, related_name="change_history")
#     field_name = models.CharField(_("Field Name"), max_length=100, null=True)
#     value_from = models.CharField(_("Value From"), max_length=100, null=True)
#     value_to = models.CharField(_("Value To"), max_length=100, null=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True, null=True)
#
#     def __str__(self):
#         return f"{self.vessel} | {self.field_name}: {self.value_from} -> {self.value_to}"
#
#     class Meta:
#         ordering = ['-created_at']
#
#
# class VesselEngine(models.Model):
#     """
#     Engine Types of Vessels are held here
#     """
#     vessel = models.ForeignKey(Vessel, on_delete=models.SET_NULL, blank=True, null=True)
#     # maker = models.ForeignKey(Maker, on_delete=models.SET_NULL, verbose_name="Maker", \
#     #                           related_name="vessel_engines_made", blank=True, null=True)
#     # maker_type = models.ForeignKey(MakerType, on_delete=models.SET_NULL, \
#     #                                verbose_name="Maker Type", related_name="maker_type_of_vessel_engine", \
#     #                                blank=True, null=True)
#     category = models.CharField(_("Category"), max_length=50, blank=True, null=True)
#     number_of_cylinders = models.IntegerField(_("Cylinders"), blank=True, null=True)
#     serial_no = models.CharField(_("Serial No"), max_length=35, blank=True, null=True)
#     description = models.CharField(_("Description"), max_length=200, blank=True, null=True)
#
#     def __str__(self):
#         data = []
#         if self.vessel:
#             data.append(self.vessel.name)
#         # if self.maker:
#         #     data.append(self.maker.name)
#         data.append(f"SN: {self.serial_no}")
#
#         return ' - '.join(data)
#
#
# class VesselBilling(models.Model):
#     """
#     Company name and address information for billings are kept in this table.
#     """
#     vessel = models.ForeignKey(Vessel, on_delete=models.SET_NULL, related_name="bills", blank=True, null=True)
#     name = models.CharField(_("Billing Name"), max_length=100)
#     country = models.CharField(_("Billing Country"), max_length=40, blank=True, null=True)
#     city = models.CharField(_("Billing City"), max_length=40, blank=True, null=True)
#     address = models.TextField(_("Address"), blank=True, null=True)
#     vat_office = models.CharField(_("Vat Office"), max_length=100, blank=True, null=True)
#     vat_no = models.CharField(_("Vat No"), max_length=20, blank=True, null=True)
#
#     def __str__(self):
#         return self.name
#
#
# class VesselBillingDefault(models.Model):
#     """
#     Vessel'larin Default Billing'leri bu tabloda tutulur.
#     """
#     vessel = models.OneToOneField(Vessel, on_delete=models.CASCADE, primary_key=True)
#     billing = models.ForeignKey(VesselBilling, on_delete=models.SET_NULL, blank=True, null=True)
#
#     def __str__(self):
#         return self.billing.name
#
#
# class VesselDefaultPIC(models.Model):
#     """
#     Vessel'larin Default Person In Contact'lari bu tabloda tutulur.
#     """
#     vessel = models.OneToOneField(Vessel, on_delete=models.CASCADE, primary_key=True)
#     pic = models.ForeignKey(Contact, on_delete=models.SET_NULL, blank=True, null=True)
#
#     def __str__(self):
#         return self.pic.get_full_name()

#
# class CompanyNote(models.Model):
#     """
#     Company ile ilgili not bu tabloda tutulur.
#     Bu tabloya ekleme muhasebe modülünden yapılacak.
#     Eklenilen not sales modülünde request oluşturulurken company seçildiğinde uyarı işareti ve bir pop-up ile gösterilecek.
#     """
#     company = models.ForeignKey(Company, on_delete=models.CASCADE)
#     note = models.TextField(_("Note"), max_length=200)
#
#     def __str__(self):
#         return self.note
