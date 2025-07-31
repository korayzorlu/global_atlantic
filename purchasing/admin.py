from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import *

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","projectNo", "supplier", "projectDate", "created_date"]
    list_display_links = ["projectNo"]
    search_fields = ["sourceCompany__name","projectNo","supplier__name", "projectDate", "created_date"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-id"]
    class Meta:
        model = Project
        
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","project","inquiryNo", "supplier", "inquiryDate", "created_date"]
    list_display_links = ["inquiryNo"]
    search_fields = ["sourceCompany__name","project__projectNo","inquiryNo","supplier__name", "inquiryDate", "created_date"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-id"]
    class Meta:
        model = Inquiry
        
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def project(self,obj):
        return obj.project.projectNo if obj.project else ""
    
@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","project","inquiry","purchaseOrderNo", "supplier", "purchaseOrderDate", "created_date"]
    list_display_links = ["purchaseOrderNo"]
    search_fields = ["sourceCompany__name","project__projectNo","inquiry__inquiryNo","purchaseOrderNo","inquiry__supplier__name", "purchaseOrderDate", "created_date"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-id"]
    class Meta:
        model = PurchaseOrder
        
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def project(self,obj):
        return obj.project.projectNo if obj.project else ""
    
    def inquiry(self,obj):
        return obj.inquiry.inquiryNo if obj.inquiry else ""
    
    def supplier(self,obj):
        return obj.inquiry.supplier.name if obj.inquiry.supplier else ""