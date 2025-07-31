from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import *

"""
@admin.register()
class Admin(admin.ModelAdmin):
    list_display = []
    list_display_links = []
    search_fields = []
    list_filter = []
    inlines = []
    ordering = []
    autocomplete_fields = []
    class Meta:
        model = 
"""


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["iso2","iso3","formal_name", "international_formal_name"]
    list_display_links = ["formal_name"]
    search_fields = ["formal_name", "international_formal_name"]
    list_filter = []
    inlines = []
    ordering = ["formal_name"]
    autocomplete_fields = []
    class Meta:
        model = Country
    
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name","country"]
    list_display_links = ["name"]
    search_fields = ["name","country__formal_name"]
    list_filter = []
    inlines = []
    ordering = ["name"]
    autocomplete_fields = ["country"]
    class Meta:
        model = City
        
    def country(self, obj):
        return obj.country.formal_name if obj.country else ""

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["id", "country", "currency", "code", "symbol"]
    list_display_links = ["currency"]
    search_fields = ["country", "currency", "code"]
    list_filter = []
    inlines = []
    ordering = ["country"]
    class Meta:
        model = Currency

admin.site.register(Person)
admin.site.register(Bank)

class PersonAdmin(admin.StackedInline):
    model = Person
    

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["id", "sourceCompany","name", "role", "companyNo", "country", "city"]
    list_display_links = ["name"]
    search_fields = ["sourceCompany__name","companyNo", "name", "role", "country__international_formal_name", "city__name"]
    list_filter = ["role"]
    inlines = [PersonAdmin]
    ordering = ["sourceCompany__name","name"]
    autocomplete_fields = ["sourceCompany","country","city"]
    class Meta:
        model = Company
        
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","name", "company"]
    list_display_links = ["name"]
    search_fields = ["sourceCompany__name","name", "company__name"]
    list_filter = []
    inlines = []
    ordering = ["sourceCompany__name","name"]
    autocomplete_fields = ["sourceCompany","company","owner"]
    class Meta:
        model = Vessel
        
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def company(self, obj):
        return obj.company.name if obj.company else ""

@admin.register(Current)
class CurrentAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","company","currency"]
    list_display_links = ["company"]
    search_fields = ["sourceCompany__name","company__name","currency__code"]
    list_filter = []
    inlines = []
    ordering = ["sourceCompany__name","company__name","currency__code"]
    autocomplete_fields = ["sourceCompany","company"]
    class Meta:
        model = Current
        
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def company(self, obj):
        return obj.company.name if obj.company else ""
    
    def currency(self, obj):
        return obj.currency.code if obj.currency else ""

admin.site.register(Owner)
@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","name","vessel"]
    list_display_links = ["name"]
    search_fields = ["sourceCompany__name","name","vessel__name"]
    list_filter = []
    inlines = []
    ordering = ["sourceCompany__name","name","vessel__name"]
    autocomplete_fields = ["sourceCompany","vessel","country","city","user"]
    class Meta:
        model = Billing
        
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def vessel(self, obj):
        return obj.vessel.name if obj.vessel else ""