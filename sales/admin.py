from django.contrib import admin

# Register your models here.
from sales.models import *
from sales.forms import ClaimsFollowUpAllFieldsForm, OrderNotConfirmationForm

# admin.site.register(Project)
# admin.site.register(Request)
# admin.site.register(RequestPart)
# admin.site.register(Inquiry)
# admin.site.register(InquiryPart)
# admin.site.register(Quotation)
# admin.site.register(QuotationPart)
# admin.site.register(OrderConfirmation)
# admin.site.register(Reason)
# admin.site.register(PurchaseOrder)
# admin.site.register(PurchaseOrderPart)
# admin.site.register(Delivery)
# admin.site.register(DeliveryTransportation)
# admin.site.register(DeliveryTax)
# admin.site.register(DeliveryInsurance)
# admin.site.register(DeliveryCustoms)
# admin.site.register(DeliveryPacking)
# admin.site.register(ProjectDocument)


# class OrderNotConfirmationAdmin(admin.ModelAdmin):
#     exclude = ['created_at','updated_at']
#     form = OrderNotConfirmationForm
    
# admin.site.register(OrderNotConfirmation, OrderNotConfirmationAdmin)

# class ClaimsFollowUpAdmin(admin.ModelAdmin):
#     exclude = ['created_at','updated_at']
#     form = ClaimsFollowUpAllFieldsForm
    
# admin.site.register(ClaimsFollowUp, ClaimsFollowUpAdmin)

# admin.site.register(ClaimReason)
# admin.site.register(ClaimResult)