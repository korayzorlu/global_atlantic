from django.urls import path, include

# from . import views
# from .views import *

from .views.incoming_invoice_views import *
from .views.send_invoice_views import *
from .views.proforma_invoice_views import *
from .views.payment_views import *
from .views.order_in_process_views import *
from .views.soa_views import *
from .views.commercial_invoice_views import *
from .views.soa_customer_views import *
from .views.soa_supplier_views import *

app_name = "account"

urlpatterns = [
    path('incoming_invoice_data/', IncomingInvoiceDataView.as_view(), name="incoming_invoice_data"),
    path('incoming_invoice_add_manual/', IncomingInvoiceManualAddView.as_view(), name = "incoming_invoice_add_manual"),
    path('incoming_invoice_add/type_<str:type>_po_<int:id>/', IncomingInvoiceAddView.as_view(), name = "incoming_invoice_add"),
    path('incoming_invoice_bulk_add/type_<str:type>_po_<str:list>/', IncomingInvoiceBulkAddView.as_view(), name = "incoming_invoice_bulk_add"),
    path('incoming_invoice_update/<int:id>/', IncomingInvoiceUpdateView.as_view(), name = "incoming_invoice_update"),
    path('incoming_invoice_delete/<str:list>', IncomingInvoiceDeleteView.as_view(), name = "incoming_invoice_delete"),
    path('incoming_invoice_pdf/<int:id>/', IncomingInvoicePdfView.as_view(), name = "incoming_invoice_pdf"),
    
    path('incoming_invoice_part_add/', IncomingInvoicePartAddView.as_view(), name = "incoming_invoice_part_add"),
    path('incoming_invoice_part_add_in_detail/i_<int:id>/', IncomingInvoicePartInDetailAddView.as_view(), name = "incoming_invoice_part_add_in_detail"),
    path('incoming_invoice_part_delete/<str:list>', IncomingInvoicePartDeleteView.as_view(), name = "incoming_invoice_part_delete"),
    
    path('incoming_invoice_expense_add_in_detail/i_<int:id>/', IncomingInvoiceExpenseInDetailAddView.as_view(), name = "incoming_invoice_expense_add_in_detail"),
    path('incoming_invoice_expense_delete/<str:list>', IncomingInvoiceExpenseDeleteView.as_view(), name = "incoming_invoice_expense_delete"),
    
    path('send_invoice_data/', SendInvoiceDataView.as_view(), name="send_invoice_data"),
    path('send_invoice_add/id_<int:id>_type_<str:type>', SendInvoiceAddView.as_view(), name="send_invoice_add"),
    path('send_invoice_pdf/<int:id>/', SendInvoicePdfView.as_view(), name = "send_invoice_pdf"),
    path('send_invoice_pdf_in_ot/<int:id>/', SendInvoicePdfInOTView.as_view(), name = "send_invoice_pdf_in_ot"),
    path('send_invoice_pdf_html/<int:id>/', SendInvoicePdfHtmlView.as_view(), name = "send_invoice_pdf_html"),
    path('send_invoice_filter_excel/', SendInvoiceFilterExcelView.as_view(), name = "send_invoice_filter_excel"),
    path('send_invoice_export_excel', SendInvoiceExportExcelView.as_view(), name = "send_invoice_export_excel"),
    path('send_invoice_download_excel/', SendInvoiceDownloadExcelView.as_view(), name = "send_invoice_download_excel"),
    path('send_invoice_fatura_pdf/<int:id>/', SendInvoiceFaturaPdfView.as_view(), name = "send_invoice_fatura_pdf"),
    
    path('send_invoice_part_currency_update/si_<int:id>_c_<int:cid>/', SendInvoicePartCurrencyUpdateView.as_view(), name = "send_invoice_part_currency_update"),
    path('send_invoice_part_delete/<str:list>', SendInvoicePartDeleteView.as_view(), name = "send_invoice_part_delete"),
    
    path('send_invoice_expense_add_in_detail/i_<int:id>/', SendInvoiceExpenseInDetailAddView.as_view(), name = "send_invoice_expense_add_in_detail"),
    path('send_invoice_expense_delete/<str:list>', SendInvoiceExpenseDeleteView.as_view(), name = "send_invoice_expense_delete"),

    path('send_invoice_update/<int:id>/', SendInvoiceUpdateView.as_view(), name = "send_invoice_update"),
    path('send_invoice_delete/<str:list>', SendInvoiceDeleteView.as_view(), name = "send_invoice_delete"),
    
    path('order_in_process_data/', OrderInProcessDataView.as_view(), name="order_in_process_data"),
    path('order_in_process_update/<int:id>/', OrderInProcessUpdateView.as_view(), name = "order_in_process_update"),
    
    path('payment_data/', PaymentDataView.as_view(), name="payment_data"),
    path('payment_add/', PaymentAddView.as_view(), name = "payment_add"),
    path('payment_current_add/c_<int:id>&<str:type>/', PaymentCurrentAddView.as_view(), name = "payment_current_add"),
    path('payment_update/<int:id>/', PaymentUpdateView.as_view(), name = "payment_update"),
    path('payment_delete/<str:list>', PaymentDeleteView.as_view(), name = "payment_delete"),
    path('payment_invoice_add_in_detail/p_<int:id>/', PaymentInvoiceInDetailAddView.as_view(), name = "payment_invoice_add_in_detail"),
    path('payment_invoice_amount/p_<int:id>/', PaymentInvoiceAmountView.as_view(), name = "payment_invoice_amount"),
    path('payment_invoice_delete/<str:list>', PaymentInvoiceDeleteView.as_view(), name = "payment_invoice_delete"),
    
    path('proforma_invoice_data/', ProformaInvoiceDataView.as_view(), name="proforma_invoice_data"),
    path('proforma_invoice_add/oc_<int:id>/', ProformaInvoiceAddView.as_view(), name="proforma_invoice_add"),
    path('service_proforma_invoice_add/ap_<int:id>/', ServiceProformaInvoiceAddView.as_view(), name="service_proforma_invoice_add"),
    path('proforma_invoice_update/<int:id>/', ProformaInvoiceUpdateView.as_view(), name = "proforma_invoice_update"),
    path('proforma_invoice_delete/<str:list>', ProformaInvoiceDeleteView.as_view(), name = "proforma_invoice_delete"),
    path('proforma_invoice_pdf/<int:id>/', ProformaInvoicePdfView.as_view(), name = "proforma_invoice_pdf"),
    
    path('proforma_invoice_part_currency_update/pi_<int:id>_c_<int:cid>/', ProformaInvoicePartCurrencyUpdateView.as_view(), name = "proforma_invoice_part_currency_update"),
    path('proforma_invoice_part_delete/<str:list>', ProformaInvoicePartDeleteView.as_view(), name = "proforma_invoice_part_delete"),
    
    path('proforma_invoice_expense_add_in_detail/i_<int:id>/', ProformaInvoiceExpenseInDetailAddView.as_view(), name = "proforma_invoice_expense_add_in_detail"),
    path('proforma_invoice_expense_delete/<str:list>', ProformaInvoiceExpenseDeleteView.as_view(), name = "proforma_invoice_expense_delete"),
    
    path('commerical_invoice_data/', CommericalInvoiceDataView.as_view(), name="commerical_invoice_data"),
    path('commerical_invoice_add/ot_<int:id>/', CommericalInvoiceAddView.as_view(), name="commerical_invoice_add"),
    path('commerical_invoice_update/<int:id>/', CommericalInvoiceUpdateView.as_view(), name = "commerical_invoice_update"),
    path('commerical_invoice_pdf/<int:id>/', CommericalInvoicePdfView.as_view(), name = "commerical_invoice_pdf"),
    path('commerical_invoice_pdf_in_ot/<int:id>/', CommericalInvoicePdfInOTView.as_view(), name = "commerical_invoice_pdf_in_ot"),
    path('commerical_invoice_delete/<str:list>', CommericalInvoiceDeleteView.as_view(), name = "commerical_invoice_delete"),
    
    path('commerical_invoice_item_delete/<str:list>', CommericalInvoiceItemDeleteView.as_view(), name = "commerical_invoice_item_delete"),
    
    path('commerical_invoice_expense_add_in_detail/i_<int:id>/', CommericalInvoiceExpenseInDetailAddView.as_view(), name = "commerical_invoice_expense_add_in_detail"),
    path('commerical_invoice_expense_delete/<str:list>', CommericalInvoiceExpenseDeleteView.as_view(), name = "commerical_invoice_expense_delete"),
    
    path('soa_data/', SOADataView.as_view(), name="soa_data"),
    path('soa_update/<int:id>/', SOAUpdateView.as_view(), name = "soa"),
    path('soa_pdf/<int:id>/', SOAPdfView.as_view(), name = "soa_pdf"),
    path('soa_incoming_pdf/<int:id>/', SOAIncomingPdfView.as_view(), name = "soa_incoming_pdf"),

    path('soa_send_invoice_filter_excel/', SOASendInvoiceFilterExcelView.as_view(), name = "soa_send_invoice_filter_excel"),
    path('soa_send_invoice_export_excel', SOASendInvoiceExportExcelView.as_view(), name = "soa_send_invoice_export_excel"),
    path('soa_send_invoice_download_excel/', SOASendInvoiceDownloadExcelView.as_view(), name = "soa_send_invoice_download_excel"),
    path('soa_send_invoice_filter_pdf/', SOASendInvoiceFilterPdfView.as_view(), name = "soa_send_invoice_filter_pdf"),
    path('soa_send_invoice_export_pdf', SOASendInvoiceExportPdfView.as_view(), name = "soa_send_invoice_export_pdf"),
    path('soa_send_invoice_download_pdf/', SOASendInvoiceDownloadPdfView.as_view(), name = "soa_send_invoice_download_pdf"),

    path('soa_incoming_invoice_filter_excel/', SOAIncomingInvoiceFilterExcelView.as_view(), name = "soa_incoming_invoice_filter_excel"),
    path('soa_incoming_invoice_export_excel', SOAIncomingInvoiceExportExcelView.as_view(), name = "soa_incoming_invoice_export_excel"),
    path('soa_incoming_invoice_download_excel/', SOAIncomingInvoiceDownloadExcelView.as_view(), name = "soa_incoming_invoice_download_excel"),
    path('soa_incoming_invoice_filter_pdf/', SOAIncomingInvoiceFilterPdfView.as_view(), name = "soa_incoming_invoice_filter_pdf"),
    path('soa_incoming_invoice_export_pdf', SOAIncomingInvoiceExportPdfView.as_view(), name = "soa_incoming_invoice_export_pdf"),
    path('soa_incoming_invoice_download_pdf/', SOAIncomingInvoiceDownloadPdfView.as_view(), name = "soa_incoming_invoice_download_pdf"),
    
    path('api/', include("account.api.urls")),
]

