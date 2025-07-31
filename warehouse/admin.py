from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import *
    
@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","name","code","country","city","address"]
    list_display_links = ["name"]
    search_fields = ["sourceCompany__name","name","code","country__international_formal_name", "city__name","address"]
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
        model = Warehouse

@admin.register(ItemGroup)
class ItemGroupAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","category","name","quantity"]
    list_display_links = ["name"]
    search_fields = ["sourceCompany__name","category","name","quantity"]
    list_filter = []
    inlines = []
    ordering = ["name"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    class Meta:
        model = ItemGroup

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","category","itemNo","name","quantity"]
    list_display_links = ["name"]
    search_fields = ["sourceCompany__name","category","itemNo","name","quantity","part__partNo","part__description"]
    list_filter = []
    inlines = []
    ordering = ["itemNo"]
    autocomplete_fields = ["part"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['part'].label_from_instance = lambda obj: f"id: {obj.id} || part no: {obj.partNo}"

        return form
    
    class Meta:
        model = Item