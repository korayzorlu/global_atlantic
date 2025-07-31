from django.urls import path, include
from rest_framework import routers

from report.api.views import *

router = routers.DefaultRouter()

#router.register(r'report_orders', ReportOrderList, "report_orders_api")

urlpatterns = [
    path('',include(router.urls)),
    path('financial_report_orders', FinancialReportOrderList.as_view(), name="financial_report_orders_api"),
    path('financial_report_order_years', FinancialReportOrderYearList.as_view(), name="financial_report_order_years_api"),
    path('financial_report_send_invoices', FinancialReportSendInvoiceList.as_view(), name="financial_report_send_invoicesapi"),
    path('financial_report_incoming_invoices', FinancialReportIncomingInvoiceList.as_view(), name="financial_report_incoming_invoicesapi"),
    path('financial_report_payment_ins', FinancialReportPaymentInList.as_view(), name="financial_report_payment_insapi"),
    path('financial_report_payment_outs', FinancialReportPaymentOutList.as_view(), name="financial_report_payment_outsapi"),
    path('financial_report_bank_halkbanks', FinancialReportBankHalkbankList.as_view(), name="financial_report_bank_halkbanksapi"),
    path('financial_report_bank_vakifbanks', FinancialReportBankVakifbankList.as_view(), name="financial_report_bank_vakifbanksapi"),
    path('financial_report_bank_isbanks', FinancialReportBankIsbankList.as_view(), name="financial_report_bank_isbanksapi"),
    path('financial_report_bank_albarakaturks', FinancialReportBankAlbarakaturkList.as_view(), name="financial_report_bank_albarakaturksapi"),
    path('financial_report_bank_emlakkatilims', FinancialReportBankEmlakkatilimList.as_view(), name="financial_report_bank_emlakkatilimsapi"),
    path('financial_report_bank_vakifkatilims', FinancialReportBankVakifkatilimList.as_view(), name="financial_report_bank_vakifkatilimsapi"),
    path('financial_report_bank_ziraatkatilims', FinancialReportBankZiraatkatilimList.as_view(), name="financial_report_bank_ziraatkatilimsapi"),
    path('financial_report_bank_totals', FinancialReportBankTotalList.as_view(), name="financial_report_bank_totals_api"),
]
