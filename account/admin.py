from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import *




@admin.register(IncomingInvoice)
class IncomingInvoiceAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "theRequest", "seller", "customerSource", "group", "incomingInvoiceNo", "incomingInvoiceDate", "created_date"]
    list_display_links = ["theRequest"]
    search_fields = ["sourceCompany__name","theRequest__requestNo","seller__name", "incomingInvoiceNo", "group"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    class Meta:
        model = IncomingInvoice
        
@admin.register(IncomingInvoicePart)
class IncomingInvoicePartAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "part_no", "description", "part_id", "quantity", "unitPrice", "totalPrice", "invoice", "project", "user"]
    list_display_links = ["part_no"]
    search_fields = ["sourceCompany__name","part__partNo", "part__description", "invoice__project__projectNo", "invoice__incomingInvoiceNo", "user__username"]
    list_filter = []
    inlines = []
    ordering = []
    autocomplete_fields = ["user", "invoice", "purchaseOrderPart", "part"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

    def project(self, obj):
        return obj.invoice.project.projectNo if obj.invoice.project else ""
    
    def part_id(self, obj):
        return obj.part.id if obj.part else ""
    
    def part_no(self, obj):
        return obj.part.partNo if obj.part else ""
    
    def description(self, obj):
        return obj.part.description if obj.part else ""

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['purchaseOrderPart'].label_from_instance = lambda obj: f"id: {obj.inquiryPart.requestPart.part.id} || part no: {obj.inquiryPart.requestPart.part.partNo} || quotation: {obj.purchaseOrder} || project: {obj.purchaseOrder.project}"

        return form
    
    class Meta:
        model = IncomingInvoicePart

@admin.register(IncomingInvoiceItem)
class IncomingInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "name", "description", "quantity", "unitPrice", "totalPrice", "invoice", "project", "user"]
    list_display_links = ["name"]
    search_fields = ["sourceCompany__name","name", "description", "invoice__project__projectNo", "invoice__incomingInvoiceNo", "user__username"]
    list_filter = []
    inlines = []
    ordering = []
    autocomplete_fields = ["user", "invoice", "purchaseOrderPart", "part"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

    def project(self, obj):
        return obj.invoice.project.projectNo if obj.invoice.project else ""

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['purchaseOrderPart'].label_from_instance = lambda obj: f"id: {obj.inquiryPart.requestPart.part.id} || part no: {obj.inquiryPart.requestPart.part.partNo} || quotation: {obj.purchaseOrder} || project: {obj.purchaseOrder.project}"

        return form
    
    class Meta:
        model = IncomingInvoiceItem

@admin.register(SendInvoice)
class SendInvoiceAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "theRequest", "seller", "customer", "group", "sendInvoiceNo", "sendInvoiceDate", "created_date"]
    list_display_links = ["theRequest"]
    search_fields = ["sourceCompany__name","theRequest__requestNo","customer__name", "sendInvoiceNo", "group"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    class Meta:
        model = SendInvoice
        

@admin.register(SendInvoiceItem)
class SendInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "name", "description", "part_id", "service_card_id", "quantity", "unitPrice", "totalPrice", "invoice", "project", "offer", "user"]
    list_display_links = ["name"]
    search_fields = ["sourceCompany__name","name", "description", "invoice__project__projectNo", "invoice__offer__offerNo", "invoice__sendInvoiceNo", "user__username"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    autocomplete_fields = ["user", "invoice", "part", "serviceCard", "quotationPart", "offerServiceCard"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

    def project(self, obj):
        return obj.invoice.project.projectNo if obj.invoice.project else ""
    
    def offer(self, obj):
        return obj.invoice.offer.offerNo if obj.invoice.offer else ""
    
    def part_id(self, obj):
        return obj.part.id if obj.part else ""
    
    def service_card_id(self, obj):
        return obj.serviceCard.id if obj.serviceCard else ""

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['quotationPart'].label_from_instance = lambda obj: f"id: {obj.inquiryPart.requestPart.part.id} || part no: {obj.inquiryPart.requestPart.part.partNo} || quotation: {obj.quotation} || project: {obj.quotation.project}"
        form.base_fields['offerServiceCard'].label_from_instance = lambda obj: f"id: {obj.serviceCard.id} || code: {obj.serviceCard.code} || offer: {obj.offer}"

        return form
    
    class Meta:
        model = SendInvoiceItem

@admin.register(SendInvoicePart)
class SendInvoicePartAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "part_no", "description", "part_id", "quantity", "unitPrice", "totalPrice", "invoice", "project", "user"]
    list_display_links = ["part_no"]
    search_fields = ["sourceCompany__name","quotationPart__inquiryPart__requestPart__part__partNo", "quotationPart__inquiryPart__requestPart__part__description", "invoice__project__projectNo", "invoice__sendInvoiceNo", "user__username"]
    list_filter = []
    inlines = []
    ordering = []
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

    def project(self, obj):
        return obj.invoice.project.projectNo if obj.invoice.project else ""
    
    def part_id(self, obj):
        return obj.quotationPart.inquiryPart.requestPart.part.id if obj.quotationPart.inquiryPart.requestPart.part else ""
    
    def part_no(self, obj):
        return obj.quotationPart.inquiryPart.requestPart.part.partNo if obj.quotationPart.inquiryPart.requestPart.part else ""
    
    def description(self, obj):
        return obj.quotationPart.inquiryPart.requestPart.part.description if obj.quotationPart.inquiryPart.requestPart.part else ""

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['quotationPart'].label_from_instance = lambda obj: f"id: {obj.inquiryPart.requestPart.part.id} || part no: {obj.inquiryPart.requestPart.part.partNo} || quotation: {obj.quotation} || project: {obj.quotation.project}"

        return form
    
    class Meta:
        model = SendInvoicePart


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "customer", "type", "sourceBank", "paymentNo", "paymentDate", "created_date"]
    list_display_links = ["customer"]
    search_fields = ["sourceCompany__name","customer__name", "type", "sourceBank__bankName", "paymentNo"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    autocomplete_fields = ["user", "customer"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    class Meta:
        model = Payment

@admin.register(PaymentInvoice)
class PaymentInvoiceAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "payment", "invoice","created_date"]
    list_display_links = ["invoice"]
    search_fields = ["sourceCompany__name","payment__paymentNo"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    autocomplete_fields = ["user", "sendInvoice", "incomingInvoice", "payment"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def payment(self, obj):
        return obj.payment.paymentNo if obj.payment else ""
    
    def invoice(self, obj):
        if obj.sendInvoice:
            return obj.sendInvoice.sendInvoiceNo
        elif obj.incomingInvoice:
            return obj.incomingInvoice.incomingInvoiceNo
    class Meta:
        model = PaymentInvoice

@admin.register(ProformaInvoice)
class ProformaInvoiceAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","theRequest", "seller", "customer", "group", "proformaInvoiceNo", "proformaInvoiceDate", "created_date"]
    list_display_links = ["theRequest"]
    search_fields = ["sourceCompany__name","theRequest"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    class Meta:
        model = ProformaInvoice

@admin.register(ProformaInvoicePart)
class ProformaInvoicePartAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "part_no", "description", "part_id", "quantity", "unitPrice", "totalPrice", "invoice", "project", "user"]
    list_display_links = ["part_no"]
    search_fields = ["sourceCompany__name","quotationPart__inquiryPart__requestPart__part__partNo", "quotationPart__inquiryPart__requestPart__part__description", "invoice__project__projectNo", "invoice__proformaInvoiceNo", "user__username"]
    list_filter = []
    inlines = []
    ordering = []
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

    def project(self, obj):
        return obj.invoice.project.projectNo if obj.invoice.project else ""
    
    def part_id(self, obj):
        return obj.quotationPart.inquiryPart.requestPart.part.id if obj.quotationPart.inquiryPart.requestPart.part else ""
    
    def part_no(self, obj):
        return obj.quotationPart.inquiryPart.requestPart.part.partNo if obj.quotationPart.inquiryPart.requestPart.part else ""
    
    def description(self, obj):
        return obj.quotationPart.inquiryPart.requestPart.part.description if obj.quotationPart.inquiryPart.requestPart.part else ""

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['quotationPart'].label_from_instance = lambda obj: f"id: {obj.inquiryPart.requestPart.part.id} || part no: {obj.inquiryPart.requestPart.part.partNo} || quotation: {obj.quotation} || project: {obj.quotation.project}"

        return form
    
    class Meta:
        model = ProformaInvoicePart

admin.site.register(ProformaInvoiceExpense)

@admin.register(CommericalInvoice)
class CommericalInvoiceAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "theRequest", "seller", "customer", "group", "commericalInvoiceNo", "commericalInvoiceDate", "created_date"]
    list_display_links = ["theRequest"]
    search_fields = ["sourceCompany__name","theRequest"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    class Meta:
        model = CommericalInvoice

@admin.register(CommericalInvoiceItem)
class CommericalInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "name", "description", "part_id", "quantity", "unitPrice", "totalPrice", "invoice", "project", "user"]
    list_display_links = ["name"]
    search_fields = ["sourceCompany__name","name", "description", "invoice__project__projectNo", "invoice__offer__offerNo", "invoice__commericalInvoiceNo", "user__username"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    autocomplete_fields = ["user", "invoice", "part", "serviceCard", "quotationPart", "offerServiceCard"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""

    def project(self, obj):
        return obj.invoice.project.projectNo if obj.invoice.project else ""
    
    def part_id(self, obj):
        return obj.part.id if obj.part else ""

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['quotationPart'].label_from_instance = lambda obj: f"id: {obj.inquiryPart.requestPart.part.id} || part no: {obj.inquiryPart.requestPart.part.partNo} || quotation: {obj.quotation} || project: {obj.quotation.project}"

        return form
    
    class Meta:
        model = CommericalInvoiceItem


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "processNo", "companyName", "sourceNo", "amount", "currency", "type", "created_date"]
    list_display_links = ["processNo"]
    search_fields = ["sourceCompany__name","processNo", "companyName", "sourceNo", "amount", "currency__code", "type"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def currency(self, obj):
        return obj.currency.code if obj.currency else ""
    class Meta:
        model = Process
        
@admin.register(ProcessStatus)
class ProcessStatusAdmin(admin.ModelAdmin):
    list_display = ["sourceCompany","id", "processStatusNo", "projectNo", "type", "created_date"]
    list_display_links = ["processStatusNo"]
    search_fields = ["sourceCompany__name","processStatusNo", "projectNo", "type"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    
    def sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ""
    
    def projectNo(self, obj):
        if obj.type == "order":
            return obj.project.projectNo if obj.project else ""
        elif obj.type == "service":
            return obj.offer.offerNo if obj.offer else ""
        elif obj.type == "purchasing":
            return obj.purchasingProject.projectNo if obj.purchasingProject else ""
    class Meta:
        model = ProcessStatus