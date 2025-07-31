from django.urls import path, include

#from . import views
from .views import *

app_name = "report"

urlpatterns = [
    path('financial_report_data/', FinancialReportDataView.as_view(), name="financial_report_data"),
    path('financial_report_filter_pdf/', FinancialReportFilterPdfView.as_view(), name = "financial_report_filter_pdf"),
    path('financial_report_export_pdf', FinancialReportExportPdfView.as_view(), name = "financial_report_export_pdf"),
    path('financial_report_download_pdf/', FinancialReportDownloadPdfView.as_view(), name = "financial_report_download_pdf"),
    
    path('api/', include("report.api.urls")),
]
