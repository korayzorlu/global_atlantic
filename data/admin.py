from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import *

@admin.register(Maker)
class MakerAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany", "id", "name"]
    list_display_links = ["name"]
    search_fields = ["name"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    class Meta:
        model = Maker
        
    
        
@admin.register(MakerType)
class MakerTypeAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "maker_name", "type"]
    list_display_links = ["type"]
    search_fields = ["maker__type", "type"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def maker_name(self, obj):
        return obj.maker.name if obj.maker else ""
    class Meta:
        model = MakerType

@admin.register(PartUnique)
class PartUniqueAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","code"]
    list_display_links = ["code"]
    search_fields = ["code"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    class Meta:
        model = PartUnique

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany", "id", "maker", "type", "partNo", "description", "techncialSpecification"]
    list_display_links = ["partNo"]
    search_fields = ["maker__name", "type__type", "partNo", "description", "techncialSpecification"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    autocomplete_fields = ['partUnique']
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    class Meta:
        model = Part

@admin.register(ServiceCard)
class ServiceCardAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany", "id", "code", "name"]
    list_display_links = ["code"]
    search_fields = ["code", "name"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    class Meta:
        model = ServiceCard


admin.site.register(Expense)