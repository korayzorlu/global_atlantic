from django.urls import path, include
from rest_framework import routers

from account.api.views import *

router = routers.DefaultRouter()
router.register(r'incoming_invoices', IncomingInvoiceList, "incoming_invoices_api")
router.register(r'incoming_invoice_parts', IncomingInvoicePartList, "incoming_invoice_parts_api")
router.register(r'incoming_invoice_expenses', IncomingInvoiceExpenseList, "incoming_invoice_expenses_api")
router.register(r'incoming_invoice_suppliers', IncomingInvoiceSupplierList, "incoming_invoice_suppliers_api")
router.register(r'send_invoices', SendInvoiceList, "send_invoices_api")
router.register(r'send_invoice_items', SendInvoiceItemList, "send_invoice_items_api")
router.register(r'send_invoice_parts', SendInvoicePartList, "send_invoice_parts_api")
router.register(r'send_invoice_expenses', SendInvoiceExpenseList, "send_invoice_expenses_api")
router.register(r'send_invoice_customers', SendInvoiceCustomerList, "send_invoice_customers_api")
router.register(r'payments', PaymentList, "payments_api")
router.register(r'payment_invoices', PaymentInvoiceList, "payment_invoices_api")
router.register(r'invoice_for_payments', InvoiceForPaymentList, "invoice_for_payments_api")
router.register(r'proforma_invoices', ProformaInvoiceList, "proforma_invoices_api")
router.register(r'proforma_invoice_items', ProformaInvoiceItemList, "proforma_invoice_items_api")
router.register(r'proforma_invoice_parts', ProformaInvoicePartList, "proforma_invoice_parts_api")
router.register(r'proforma_invoice_expenses', ProformaInvoiceExpenseList, "proforma_invoice_expenses_api")
router.register(r'commerical_invoices', CommericalInvoiceList, "commerical_invoices_api")
router.register(r'commerical_invoice_items', CommericalInvoiceItemList, "commerical_invoice_items_api")
router.register(r'commerical_invoice_expenses', CommericalInvoiceExpenseList, "commerical_invoice_expenses_api")
router.register(r'processes', ProcessList, "processes_api")
router.register(r'process_statuses', ProcessStatusList, "process_statuses_api")

urlpatterns = [
    path('',include(router.urls)),
    path('order_in_processes', OrderInProcessList.as_view(), name="order_in_processes_api"),
    path('send_invoices_multiple', SendInvoiceMultipleList.as_view(), name="send_invoices_multiple_api"),
    path('proforma_invoices_multiple', ProformaInvoiceMultipleList.as_view(), name="proforma_invoices_multiple_api"),
    path('soa_multiple', SOAMultipleList.as_view(), name="soa_multiple_api"),
    path('current_totals/', CurrentTotalList.as_view(), name="current_totals_api"),
    path('send_invoice_totals/', SendInvoiceTotalList.as_view(), name="send_invoice_totals_api"),
    path('incoming_invoice_totals/', IncomingInvoiceTotalList.as_view(), name="incoming_invoice_totals_api"),
]