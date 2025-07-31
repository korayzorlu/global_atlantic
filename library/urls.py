from django.urls import path, include

from . import views
from .views import *

app_name = "library"

urlpatterns = [
    path('library_data/', LibraryDataView.as_view(), name="library_data"),
    path('sale_documents_data/', SaleDocumentsDataView.as_view(), name="sale_documents_data"),
    path('sale_documents_pdf/<str:level>_<str:name>/', views.SaleDocumentsPdfView.as_view(), name = "sale_documents_pdf"),
    
    path('api/', include("library.api.urls")),
]
