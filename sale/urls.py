from django.urls import path, include

#from . import views
#from .views import *
from .views.main_views import *
from .views.request_views import *
from .views.inquiry_views import *
from .views.quotation_views import *
from .views.order_confirmation_views import *
from .views.order_not_confirmation_views import *
from .views.purchase_order_views import *
from .views.order_tracking_views import *
from .views.manager_approval_views import *
from .views.order_in_process_views import *
from .views.main_views import *
from .views.dispatch_order_views import *

app_name = "sale"

urlpatterns = [
    path('request_data/', RequestDataView.as_view(), name="request_data"),
    path('request_add/', RequestAddView.as_view(), name = "request_add"),
    path('request_update/<int:id>/', RequestUpdateView.as_view(), name = "request_update"),
    path('request_delete/<str:list>/', RequestDeleteView.as_view(), name = "request_delete"),
    path('request_pdf/<int:id>/', RequestPdfView.as_view(), name = "request_pdf"),
    
    path('request_part_add/', RequestPartAddView.as_view(), name = "request_part_add"),
    path('request_part_reorder/r_<int:theRequestId>_p_<str:id>_old_<str:old>_new_<str:new>', RequestPartReorderView.as_view(), name = "request_part_reorder"),
    path('request_part_add_in_detail/r_<int:id>/', RequestPartInDetailAddView.as_view(), name = "request_part_add_in_detail"),
    path('request_part_update/<int:id>/', RequestPartUpdateView.as_view(), name = "request_part_update"),
    path('request_part_quantity_duplicate/<int:id>', RequestPartQuantityDuplicateView.as_view(), name = "request_part_quantity_duplicate"),
    path('request_part_add_to_inquiry/<int:id>/', RequestPartAddToInquiryView.as_view(), name = "request_part_delete"),
    path('request_part_delete/<str:list>', RequestPartDeleteView.as_view(), name = "request_part_delete"),
    
    path('inquiry_data/', InquiryDataView.as_view(), name="inquiry_data"),
    path('inquiry_add/r_<int:id>/', InquiryAddView.as_view(), name = "inquiry_add"),
    path('inquiry_update/<int:id>/', InquiryUpdateView.as_view(), name = "inquiry_update"),
    path('inquiry_delete/<str:list>/', InquiryDeleteView.as_view(), name = "inquiry_delete"),
    path('inquiry_pdf/<int:id>_s_<str:source>/', InquiryPdfView.as_view(), name = "inquiry_pdf"),
    path('inquiry_pdf_make/<int:id>', InquiryPdfMakeView.as_view(), name = "inquiry_pdf_make"),
    
    path('inquiry_part_update/<int:id>/', InquiryPartUpdateView.as_view(), name = "inquiry_part_update"),
    path('inquiry_part_quantity_duplicate/<int:id>', InquiryPartQuantityDuplicateView.as_view(), name = "inquiry_part_quantity_duplicate"),
    path('inquiry_part_availability_duplicate/<int:id>', InquiryPartAvailabilityDuplicateView.as_view(), name = "inquiry_part_availability_duplicate"),
    path('inquiry_part_delete/<str:list>', InquiryPartDeleteView.as_view(), name = "inquiry_part_delete"),
    
    path('quotation_data/', QuotationDataView.as_view(), name="quotation_data"),
    path('quotation_add/i_<int:id>/', QuotationAddView.as_view(), name = "quotation_add"),
    path('quotation_update/<int:id>/', QuotationUpdateView.as_view(), name = "quotation_update"),
    path('quotation_revision/<int:id>/', QuotationRevisionView.as_view(), name = "quotation_revision"),
    path('quotation_delete/<str:list>/', QuotationDeleteView.as_view(), name = "quotation_delete"),
    path('quotation_pdf/<int:id>_s_<str:source>/', QuotationPdfView.as_view(), name = "quotation_pdf"),
    path('quotation_all_excel/', QuotationAllExcelView.as_view(), name = "quotation_all_excel"),
    path('quotation_daily_excel/', QuotationDailyExcelView.as_view(), name = "quotation_daily_excel"),
    path('quotation_excel/<int:id>/', QuotationExcelView.as_view(), name = "quotation_excel"),
    path('quotation_filter_excel/', QuotationFilterExcelView.as_view(), name = "quotation_filter_excel"),
    path('quotation_export_excel', QuotationExportExcelView.as_view(), name = "quotation_export_excel"),
    path('quotation_download_excel/', QuotationDownloadExcelView.as_view(), name = "quotation_download_excel"),
    path('quotation_buying_total/', QuotationBuyingTotalView.as_view(), name = "quotation_buying_total"),
    
    path('quotation_part_add_in_detail/q_<int:id>/', QuotationPartInDetailAddView.as_view(), name = "quotation_part_add_in_detail"),
    path('quotation_part_reorder/q_<int:quotationId>_p_<str:id>_old_<str:old>_new_<str:new>', QuotationPartReorderView.as_view(), name = "quotation_part_reorder"),
    path('quotation_part_update/<int:id>/', QuotationPartUpdateView.as_view(), name = "quotationsy_part_update"),
    path('quotation_part_bulk_update/qp_<str:list>_c_<int:id>/', QuotationPartBulkUpdateView.as_view(), name = "quotation_part_bulk_update"),
    path('quotation_part_profit_duplicate/<int:id>', QuotationPartProfitDuplicateView.as_view(), name = "quotation_part_profit_duplicate"),
    path('quotation_part_discount_duplicate/<int:id>', QuotationPartDiscountDuplicateView.as_view(), name = "quotation_part_discount_duplicate"),
    path('quotation_part_availability_duplicate/<int:id>', QuotationPartAvailabilityDuplicateView.as_view(), name = "quotation_part_availability_duplicate"),
    path('quotation_part_note_duplicate/<int:id>', QuotationPartNoteDuplicateView.as_view(), name = "quotation_part_note_duplicate"),
    path('quotation_part_remark_duplicate/<int:id>', QuotationPartRemarkDuplicateView.as_view(), name = "quotation_part_remark_duplicate"),
    path('quotation_part_source/', QuotationPartSourceView.as_view(), name = "quotation_part_source"),
    path('quotation_part_delete/<str:list>', QuotationPartDeleteView.as_view(), name = "quotation_part_delete"),
    
    path('quotation_extra_add_in_detail/i_<int:id>/', QuotationExtraInDetailAddView.as_view(), name = "quotation_extra_add_in_detail"),
    path('quotation_extra_delete/<str:list>', QuotationExtraDeleteView.as_view(), name = "quotation_extra_delete"),
    
    path('order_confirmation_data/', OrderConfirmationDataView.as_view(), name="order_confirmation_data"),
    path('order_confirmation_add/q_<int:id>/', OrderConfirmationAddView.as_view(), name = "order_confirmation_add"),
    path('order_confirmation_update/<int:id>/', OrderConfirmationUpdateView.as_view(), name = "order_confirmation_update"),
    path('order_confirmation_delete/<str:list>/', OrderConfirmationDeleteView.as_view(), name = "order_confirmation_delete"),
    path('order_confirmation_pdf/<int:id>_s_<str:source>/', OrderConfirmationPdfView.as_view(), name = "order_confirmation_pdf"),
    path('order_confirmation_all_excel/', OrderConfirmationAllExcelView.as_view(), name = "order_confirmation_all_excel"),
    path('order_confirmation_daily_excel/', OrderConfirmationDailyExcelView.as_view(), name = "order_confirmation_daily_excel"),
    path('order_confirmation_filter_excel/', OrderConfirmationFilterExcelView.as_view(), name = "order_confirmation_filter_excel"),
    path('order_confirmation_export_excel', OrderConfirmationExportExcelView.as_view(), name = "order_confirmation_export_excel"),
    path('order_confirmation_download_excel/', OrderConfirmationDownloadExcelView.as_view(), name = "order_confirmation_download_excel"),
    
    path('order_not_confirmation_data/', OrderNotConfirmationDataView.as_view(), name="order_not_confirmation_data"),
    path('order_not_confirmation_update/<int:id>/', OrderNotConfirmationUpdateView.as_view(), name = "order_not_confirmation_update"),
    path('order_not_confirmation_delete/<str:list>/', OrderNotConfirmationDeleteView.as_view(), name = "order_not_confirmation_delete"),
    path('order_not_confirmation_pdf/<int:id>/', OrderNotConfirmationPdfView.as_view(), name = "order_not_confirmation_pdf"),
    
    path('order_in_process_data/', OrderInProcessDataView.as_view(), name="order_in_process_data"),
    path('order_in_process_update/<int:id>/', OrderInProcessUpdateView.as_view(), name = "order_in_process_update"),
    
    path('purchase_order_data/', PurchaseOrderDataView.as_view(), name="purchase_order_data"),
    path('purchase_order_add/oc_<int:id>_<str:listt>/', PurchaseOrderAddView.as_view(), name = "purchase_order_add"),
    path('purchase_order_update/<int:id>/', PurchaseOrderUpdateView.as_view(), name = "purchase_order_update"),
    path('purchase_order_delete/<str:list>/', PurchaseOrderDeleteView.as_view(), name = "purchase_order_delete"),
    path('purchase_order_pdf/<int:id>_s_<str:source>/', PurchaseOrderPdfView.as_view(), name = "purchase_order_pdf"),
    path('purchase_order_excel/', PurchaseOrderAllExcelView.as_view(), name = "purchase_order_excel"),
    path('purchase_order_export_excel', PurchaseOrderExportExcelView.as_view(), name = "purchase_order_export_excel"),
    path('purchase_order_download_excel/', PurchaseOrderDownloadExcelView.as_view(), name = "purchase_order_download_excel"),
    
    path('purchase_order_part_update/<int:id>/', PurchaseOrderPartUpdateView.as_view(), name = "purchase_order_part_update"),
    
    path('order_tracking_data/', OrderTrackingDataView.as_view(), name="order_tracking_data"),
    path('order_tracking_add/po_<int:id>/', OrderTrackingAddView.as_view(), name = "order_tracking_add"),
    path('order_tracking_update/<int:id>/', OrderTrackingUpdateView.as_view(), name = "order_tracking_update"),
    path('order_tracking_delete/<str:list>/', OrderTrackingDeleteView.as_view(), name = "order_tracking_delete"),
    
    path('order_tracking_document/<int:id>/', OrderTrackingDocumentView.as_view(), name = "order_tracking_document"),
    path('order_tracking_document_add/ot_<int:id>/', OrderTrackingDocumentAddView.as_view(), name = "order_tracking_document_add"),
    path('order_tracking_document_delete/<int:id>/', OrderTrackingDocumentDeleteView.as_view(), name = "order_tracking_document_delete"),
    path('order_tracking_documents/<str:file>/', OrderTrackingDocumentsView.as_view(), name = "order_tracking_documents"),
    path('order_tracking_pdf/<str:type>_<int:id>/', OrderTrackingPdfView.as_view(), name = "order_tracking_pdf"),
    path('commerical_invoice_pdf/oc_<int:id>/', CommericalInvoicePdfView.as_view(), name = "commerical_invoice_pdf"),
    path('order_tracking_document_pdf/<int:id>_<str:name>/', OrderTrackingDocumentPdfView.as_view(), name = "order_tracking_document_pdf"),
    
    path('delivery_add_in_detail/ot_<int:id>/', DeliveryInDetailAddView.as_view(), name = "delivery_add_in_detail"),

    path('dispatch_order_data/', DispatchOrderDataView.as_view(), name="dispatch_order_data"),
    path('dispatch_order_add/ot_<int:id>/', DispatchOrderAddView.as_view(), name = "dispatch_order_add"),
    path('dispatch_order_add_manual/', DispatchOrderAddManualView.as_view(), name = "dispatch_order_add_manual"),
    path('dispatch_order_update/<int:id>/', DispatchOrderUpdateView.as_view(), name = "dispatch_order_update"),
    path('dispatch_order_delete/<str:list>/', DispatchOrderDeleteView.as_view(), name = "dispatch_order_delete"),
    
    path('manager_approval_data/', ManagerApprovalDataView.as_view(), name="manager_approval_data"),
    path('manager_approval_update/<int:id>/', ManagerApprovalUpdateView.as_view(), name = "manager_approval_update"),
    path('manager_approval_update_in_dashboard/<int:id>/', ManagerApprovalUpdateInDashboardView.as_view(), name = "manager_approval_update_in_dashboard"),
    path('manager_approval_update_in_table_confirm/<int:id>', ManagerApprovalUpdateInTableConfirmView.as_view(), name = "manager_approval_update_in_table_confirm"),
    path('manager_approval_update_in_table_not_confirm/<int:id>', ManagerApprovalUpdateInTableNotConfirmView.as_view(), name = "manager_approval_update_in_table_not_confirm"),
    
    path('email_send/<str:type>_<int:id>/', EmailSendView.as_view(), name = "email_send"),
    
    path('api/', include("sale.api.urls")),
]
