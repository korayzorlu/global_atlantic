from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import *

admin.site.register(Project)

class InquiryAdmin(admin.StackedInline):
    model = Inquiry
    
class RequestPartAdmin(admin.StackedInline):
    fields = ["id", "part", "quantity"]
    model = RequestPart

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","project", "requestNo", "customer", "vessel", "person", "maker", "makerType", "requestDate", "created_date"]
    list_display_links = ["requestNo"]
    search_fields = ["sourceCompany__name","requestNo","customer__name", "vessel__name", "maker__name", "makerType__name", "requestDate", "created_date"]
    list_filter = ["created_date"]
    inlines = [InquiryAdmin]
    ordering = ["-pk"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    class Meta:
        model = Request
@admin.register(RequestPart)
class RequestPartAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "part", "maker_name", "makerType_type", "description", "technicalSpecification", "part_id", "quantity", "theRequest", "sequency", "user"]
    list_display_links = ["part"]
    search_fields = ["sourceCompany__name","part__partNo", "part__description", "theRequest__requestNo", "part__maker__name"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    autocomplete_fields = ["user", "theRequest", "part"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def maker_name(self, obj):
        return obj.part.maker.name if obj.part.maker else ""
    
    def makerType_type(self, obj):
        return obj.part.type.type if obj.part.type else ""
    
    def description(self, obj):
        return obj.part.description
    
    def technicalSpecification(self, obj):
        return obj.part.techncialSpecification
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['part'].label_from_instance = lambda obj: f"id: {obj.id} || part no: {obj.partNo}"

        return form

    class Meta:
        model = RequestPart

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "project", "inquiryNo", "supplier", "inquiryDate", "created_date"]
    list_display_links = ["inquiryNo"]
    search_fields = ["sourceCompany__name","inquiryNo", "project__projectNo", "supplier__name"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    class Meta:
        model = Inquiry

@admin.register(InquiryPart)
class InquiryPartAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "part_no", "maker_name", "makerType_type", "description", "part_id", "quantity", "inquiry", "sequency", "project", "user"]
    list_display_links = ["part_no"]
    search_fields = ["sourceCompany__name","requestPart__part__partNo", "requestPart__part__description", "inquiry__project__projectNo", "inquiry__inquiryNo", "user__username"]
    list_filter = []
    inlines = []
    autocomplete_fields = ["maker", "makerType", "user", "inquiry", "requestPart"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

    def project(self, obj):
        return obj.inquiry.project.projectNo if obj.inquiry.project else ""
    
    def maker_name(self, obj):
        return obj.requestPart.part.maker.name if obj.requestPart.part.maker else ""
    
    def makerType_type(self, obj):
        return obj.requestPart.part.type.type if obj.requestPart.part.type else ""
    
    def part_id(self, obj):
        return obj.requestPart.part.id if obj.requestPart.part else ""
    
    def part_no(self, obj):
        return obj.requestPart.part.partNo if obj.requestPart.part else ""
    
    def description(self, obj):
        return obj.requestPart.part.description if obj.requestPart.part else ""
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['requestPart'].label_from_instance = lambda obj: f"id: {obj.part.id} || part no: {obj.part.partNo} || inquiry: {obj.theRequest}"

        return form
    
    class Meta:
        model = InquiryPart

# class QuotationPartAdmin(admin.StackedInline):
#     model = QuotationPart
    
@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","quotationNo", "project", "customer", "vessel", "person", "approval", "quotationDate", "created_date"]
    list_display_links = ["quotationNo"]
    search_fields = ["sourceCompany__name","quotationNo", "project__projectNo", "inquiry__theRequest__customer__name", "approval"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def customer(self, obj):
        return obj.inquiry.theRequest.customer  # C modelinin A modeline bağlı alanını döndüren fonksiyon
    
    def vessel(self, obj):
        return obj.inquiry.theRequest.vessel
    
    def person(self, obj):
        return obj.inquiry.theRequest.person

    class Meta:
        model = Quotation

@admin.register(QuotationPart)
class QuotationPartAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "part_no", "maker_name", "makerType_type", "description", "part_id", "quantity", "quotation", "project", "user"]
    list_display_links = ["part_no"]
    search_fields = ["sourceCompany__name","inquiryPart__requestPart__part__partNo", "inquiryPart__requestPart__part__description", "quotation__project__projectNo", "quotation__quotationNo", "user__username"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    autocomplete_fields = ["maker", "makerType", "user", "quotation", "inquiryPart"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

    def project(self, obj):
        return obj.quotation.project.projectNo if obj.quotation.project else ""
    
    def maker_name(self, obj):
        return obj.inquiryPart.requestPart.part.maker.name if obj.inquiryPart.requestPart.part.maker else ""
    
    def makerType_type(self, obj):
        return obj.inquiryPart.requestPart.part.type.type if obj.inquiryPart.requestPart.part.type else ""
    
    def part_id(self, obj):
        return obj.inquiryPart.requestPart.part.id if obj.inquiryPart.requestPart.part else ""
    
    def part_no(self, obj):
        return obj.inquiryPart.requestPart.part.partNo if obj.inquiryPart.requestPart.part else ""
    
    def description(self, obj):
        return obj.inquiryPart.requestPart.part.description if obj.inquiryPart.requestPart.part else ""

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['inquiryPart'].label_from_instance = lambda obj: f"id: {obj.requestPart.part.id} || part no: {obj.requestPart.part.partNo} || inquiry: {obj.inquiry} || project: {obj.inquiry.project}"

        return form
    
    class Meta:
        model = QuotationPart
        
admin.site.register(QuotationExtra)  

@admin.register(OrderConfirmation)
class OrderConfirmationAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","orderConfirmationNo", "project", "customer", "vessel", "person", "orderConfirmationDate", "created_date"]
    list_display_links = ["orderConfirmationNo"]
    search_fields = ["sourceCompany__name","orderConfirmationNo", "project__projectNo", "quotation__inquiry__theRequest__customer__name", "quotation__inquiry__theRequest__vessel__name"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def customer(self, obj):
        return obj.quotation.inquiry.theRequest.customer  # C modelinin A modeline bağlı alanını döndüren fonksiyon
    
    def vessel(self, obj):
        return obj.quotation.inquiry.theRequest.vessel
    
    def person(self, obj):
        return obj.quotation.inquiry.theRequest.person

    class Meta:
        model = OrderConfirmation
        
admin.site.register(OrderNotConfirmation)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","purchaseOrderNo", "project", "supplier", "person", "purchaseOrderDate", "created_date"]
    list_display_links = ["purchaseOrderNo"]
    search_fields = ["sourceCompany__name","purchaseOrderNo", "project__projectNo", "inquiry__supplier__name"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def supplier(self, obj):
        return obj.inquiry.supplier
    
    def person(self, obj):
        return obj.inquiry.theRequest.person

    class Meta:
        model = PurchaseOrder

@admin.register(PurchaseOrderPart)
class PurchaseOrderPartAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "part_no", "maker_name", "makerType_type", "description", "part_id", "quantity", "purchaseOrder", "project", "user"]
    list_display_links = ["part_no"]
    search_fields = ["sourceCompany__name","inquiryPart__requestPart__part__partNo", "inquiryPart__requestPart__part__description", "purchaseOrder__project__projectNo", "purchaseOrder__purchaseOrderNo", "user__username"]
    list_filter = []
    inlines = []
    autocomplete_fields = ["maker", "makerType", "user", "purchaseOrder", "inquiryPart"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

    def project(self, obj):
        return obj.inquiryPart.inquiry.project.projectNo if obj.inquiryPart.inquiry.project else ""
    
    def maker_name(self, obj):
        return obj.inquiryPart.requestPart.part.maker.name if obj.inquiryPart.requestPart.part.maker else ""
    
    def makerType_type(self, obj):
        return obj.inquiryPart.requestPart.part.type.type if obj.inquiryPart.requestPart.part.type else ""
    
    def part_id(self, obj):
        return obj.inquiryPart.requestPart.part.id if obj.inquiryPart.requestPart.part else ""
    
    def part_no(self, obj):
        return obj.inquiryPart.requestPart.part.partNo if obj.inquiryPart.requestPart.part else ""
    
    def description(self, obj):
        return obj.inquiryPart.requestPart.part.description if obj.inquiryPart.requestPart.part else ""

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['inquiryPart'].label_from_instance = lambda obj: f"id: {obj.requestPart.part.id} || part no: {obj.requestPart.part.partNo} || inquiry: {obj.inquiry} || project: {obj.inquiry.project}"

        return form
    
    class Meta:
        model = PurchaseOrderPart

admin.site.register(OrderTracking)

@admin.register(OrderTrackingDocument)
class OrderTrackingDocumentAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "name", "file", "orderTracking", "user"]
    list_display_links = ["name"]
    search_fields = ["sourceCompany__name","file", "orderTracking__orderTrackingNo", "user__username"]
    list_filter = []
    inlines = []
    ordering = []
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    class Meta:
        model = OrderTrackingDocument

admin.site.register(Collection)
admin.site.register(CollectionPart)
@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","orderTracking", "orderConfirmation", "trackingNo"]
    list_display_links = ["orderTracking"]
    search_fields = ["sourceCompany__name"]
    list_filter = []
    inlines = []
    ordering = []
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

    class Meta:
        model = Delivery

@admin.register(DispatchOrder)
class DispatchOrderAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","dispatchOrderNo", "orderTracking", "dispatchOrderDate", "created_date"]
    list_display_links = ["dispatchOrderNo"]
    search_fields = ["sourceCompany__name","dispatchOrderNo", "orderTracking__orderTrackingNo"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def orderTracking(self, obj):
        return obj.orderTracking

    class Meta:
        model = DispatchOrder

@admin.register(DispatchOrderPart)
class DispatchOrderPartAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "part_no", "maker_name", "makerType_type", "description", "part_id", "quantity", "dispatchOrder","orderTracking", "user"]
    list_display_links = ["part_no"]
    search_fields = [
        "sourceCompany__name",
        "collectionPart__purchaseOrderPart__inquiryPart__requestPart__part__partNo",
        "collectionPart__purchaseOrderPart__inquiryPart__requestPart__part__description",
        "dispatchOrder__orderTracking__project__projectNo",
        "dispatchOrder__dispatchOrderNo",
        "user__username"
    ]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    autocomplete_fields = ["user", "dispatchOrder"]
    
    def sourceCompany(self,obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def dispatchOrder(self, obj):
        return obj.dispatchOrder if obj.dispatchOrder else ""

    def orderTracking(self, obj):
        return obj.orderTracking.orderTrackingNo if obj.orderTracking else ""
    
    def maker_name(self, obj):
        return obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.maker.name if obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.maker else ""
    
    def makerType_type(self, obj):
        return obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.type.type if obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.type else ""
    
    def part_id(self, obj):
        return obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.id if obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part else ""
    
    def part_no(self, obj):
        return obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.partNo if obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part else ""
    
    def description(self, obj):
        return obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.description if obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part else ""

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['collectionPart'].label_from_instance = lambda obj: f"id: {obj.purchaseOrderPart.inquiryPart.requestPart.part.id} || part no: {obj.purchaseOrderPart.inquiryPart.requestPart.part.partNo} || orderTracking: {obj.collection.orderTracking}"

        return form
    
    class Meta:
        model = DispatchOrderPart