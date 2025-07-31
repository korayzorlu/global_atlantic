from django.urls import path

from library.api.views import *

urlpatterns = [
    path('sale_documents', SaleDocumentsList.as_view(), name="sale_documents_api"),
]
