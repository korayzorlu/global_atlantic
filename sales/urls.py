from django.urls import path, include

from .views import *

app_name = "sales"

urlpatterns = [
    path('project_create/', ProjectCreateView.as_view(), name="project_create"),
    path('project/<int:project_id>/continue/', ProjectContinueView.as_view(), name="project_continue"),

    path('project/<int:project_id>/request/', ProjectRequestView.as_view(), name="project_request"),
    path('project/<int:project_id>/request/pdf/', ProjectRequestPDFView.as_view(), name="project_request_pdf"),
    path('project/<int:project_id>/request/excel/', ProjectRequestExcelView.as_view(), name="project_request_excel"),

    path('project/<int:project_id>/inquiry/', ProjectInquiryView.as_view(), name="project_inquiry"),
    path('project/<int:project_id>/inquiry/<int:inquiry_id>/pdf/', ProjectInquiryPDFView.as_view(),
         name="project_inquiry_pdf"),
    path('project/<int:project_id>/inquiry/<int:inquiry_id>/excel/', ProjectInquiryExcelView.as_view(),
         name="project_inquiry_excel"),

    path('project/<int:project_id>/quotation/', ProjectQuotationView.as_view(), name="project_quotation"),
    path('project/<int:project_id>/quotation/<int:quotation_id>', ProjectQuotationView.as_view(), name="project_quotation_notification"),
    path('project/<int:project_id>/quotation/<int:quotation_id>/pdf/', ProjectQuotationPDFView.as_view(),
         name="project_quotation_pdf"),
    path('project/<int:project_id>/quotation/<int:quotation_id>/excel/', ProjectQuotationExcelView.as_view(),
         name="project_quotation_excel"),
    path('project/<int:project_id>/order_confirmation/<int:confirmation_pk>/pdf/',
         ProjectOrderConfirmationPDFView.as_view(), name="project_order_confirmation_pdf"),
    path('project/<int:project_id>/order_confirmation/<int:confirmation_pk>/excel/',
         ProjectOrderConfirmationExcelView.as_view(), name="project_order_confirmation_excel"),

    path('project/<int:project_id>/purchase_order/', ProjectPurchaseOrderView.as_view(), name="project_purchase_order"),
    path('project/<int:project_id>/purchase_order/<int:purchase_order_id>/pdf/',
         ProjectPurchaseOrderPDFView.as_view(), name="project_purchase_order_pdf"),
    path('project/<int:project_id>/purchase_order/<int:purchase_order_id>/excel/',
         ProjectPurchaseOrderExcelView.as_view(), name="project_purchase_order_excel"),

    path('project/<int:project_id>/delivery/', ProjectDeliveryView.as_view(), name="project_delivery"),

    path('sales_data/', SalesDataView.as_view(), name="sales_data"),
    
    path('not_confirmed_quotation/', NotConfirmedQuotationView.as_view(), name="not_confirmed_quotation"),
    
    path('notconfirmation/<int:project_id>/continue/', NotConfirmedProjectContinueView.as_view(), name="not_confirmed_quotation_continue"),
    path('notconfirmation/<int:project_id>/request/', ProjectRequestView.as_view(), name="notconfirmation_request"),
    path('notconfirmation/<int:project_id>/request/pdf/', ProjectRequestPDFView.as_view(), name="notconfirmation_request_pdf"),
    path('notconfirmation/<int:project_id>/request/excel/', ProjectRequestExcelView.as_view(), name="notconfirmation_request_excel"),
    
    path('notconfirmation/<int:project_id>/inquiry/', ProjectInquiryView.as_view(), name="notconfirmation_inquiry"),
    path('notconfirmation/<int:project_id>/inquiry/<int:inquiry_id>/pdf/', ProjectInquiryPDFView.as_view(),
         name="notconfirmation_inquiry_pdf"),
    path('notconfirmation/<int:project_id>/inquiry/<int:inquiry_id>/excel/', ProjectInquiryExcelView.as_view(),
         name="notconfirmation_inquiry_excel"),


    path('notconfirmation/<int:project_id>/quotation/', ProjectQuotationView.as_view(), name="notconfirmation_quotation"),
     path('notconfirmation/<int:project_id>/quotation/<int:quotation_id>/pdf/', ProjectQuotationPDFView.as_view(),
         name="notconfirmation_quotation_pdf"),
    path('notconfirmation/<int:project_id>/quotation/<int:quotation_id>/excel/', ProjectQuotationExcelView.as_view(),
         name="notconfirmation_quotation_excel"),


    path('claims_follow_up/', ClaimsFollowUpView.as_view(), name="claims_follow_up"),
    path('claims_follow_up/<int:claim_id>', ClaimsFollowUpDetailView.as_view(), name="claims_follow_up_detail"),
    path('order_status/', OrderStatusView.as_view(), name="order_status"),
    path('api/', include("sales.api.urls")),
]
