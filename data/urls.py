from django.urls import path, include

from . import views
from .views.expense_views import *
from .views.maker_type_views import *
from .views.maker_views import *
from .views.part_views import *
from .views.service_card_views import *

app_name = "data"

urlpatterns = [
    path('maker_data/', MakerDataView.as_view(), name="maker_data"),
    path('maker_add/', MakerAddView.as_view(), name = "maker_add"),
    path('maker_bulk_add/', MakerBulkAddView.as_view(), name = "maker_bulk_add"),
    path('maker_update/<int:id>/', MakerUpdateView.as_view(), name = "maker_update"),
    path('maker_delete/<str:list>/', MakerDeleteView.as_view(), name = "maker_delete"),
    path('maker_bulk_add_excel/', MakerBulkAddExcelView.as_view(), name = "maker_bulk_add_excel"),
    
    path('maker_type_add/', MakerTypeAddView.as_view(), name = "maker_type_add"),
    path('maker_type_add_in_detail/', MakerTypeInDetailAddView.as_view(), name = "maker_type_add_in_detail"),
    path('maker_type_bulk_add/', MakerTypeBulkAddView.as_view(), name = "maker_type_bulk_add"),
    path('maker_type_update/<int:id>/', MakerTypeUpdateView.as_view(), name = "maker_type_update"),
    path('maker_type_delete/<str:list>', MakerTypeDeleteView.as_view(), name = "maker_type_delete"),
    path('maker_type_bulk_add_excel/', MakerTypeBulkAddExcelView.as_view(), name = "maker_type_bulk_add_excel"),
    
    path('part_data/', PartDataView.as_view(), name = "part_data"),
    path('part_add/', PartAddView.as_view(), name = "part_add"),
    path('part_update/<int:id>/', PartUpdateView.as_view(), name = "part_update"),
    path('part_delete/<str:list>/', PartDeleteView.as_view(), name = "part_delete"),
    path('part_filter_excel/', PartFilterExcelView.as_view(), name = "part_filter_excel"),
    path('part_export_excel', PartExportExcelView.as_view(), name = "part_export_excel"),
    path('part_download_excel/', PartDownloadExcelView.as_view(), name = "part_download_excel"),
    
    path('part_document/<int:id>/', PartDocumentView.as_view(), name = "part_document"),
    path('part_image_add/p_<int:id>/', PartImageAddView.as_view(), name = "part_image_add"),
    path('part_image_delete/<int:id>/', PartImageDeleteView.as_view(), name = "part_image_delete"),
    
    path('part_unique_data/', PartUniqueDataView.as_view(), name = "part_unique_data"),
    path('part_unique_add/', PartUniqueAddView.as_view(), name = "part_unique_add"),
    path('part_unique_update/<int:id>/', PartUniqueUpdateView.as_view(), name = "part_unique_update"),
    path('part_unique_delete/<int:id>/', PartUniqueDeleteView.as_view(), name = "part_unique_delete"),
    
    path('service_card_data/', ServiceCardDataView.as_view(), name="service_card_data"),
    path('service_card_add/', ServiceCardAddView.as_view(), name = "service_card_add"),
    path('service_card_update/<int:id>/', ServiceCardUpdateView.as_view(), name = "service_card_update"),
    path('service_card_delete/<str:list>/', ServiceCardDeleteView.as_view(), name = "service_card_delete"),
    
    path('expense_data/', ExpenseDataView.as_view(), name="expense_data"),
    path('expense_add/', ExpenseAddView.as_view(), name = "expense_add"),
    path('expense_update/<int:id>/', ExpenseUpdateView.as_view(), name = "expense_update"),
    path('expense_delete/<str:list>/', ExpenseDeleteView.as_view(), name = "expense_delete"),
    
    path('api/', include("data.api.urls")),
]
