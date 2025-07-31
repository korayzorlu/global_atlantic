from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import *
    
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name","companyNo","country","city"]
    list_display_links = ["name"]
    search_fields = ["name", "companyNo","country__international_formal_name", "city__name"]
    list_filter = []
    inlines = []
    ordering = ["name"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def country(self,obj):
        return obj.country.international_formal_name if obj.country else ""
    
    def city(self,obj):
        return obj.city.name if obj.city else ""
    class Meta:
        model = Company
        
@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ["bankName", "company", "currency"]
    list_display_links = ["bankName"]
    search_fields = ["bankName", "company"]
    list_filter = []
    inlines = []
    ordering = ["bankName"]
    class Meta:
        model = Bank