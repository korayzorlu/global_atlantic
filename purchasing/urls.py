from django.urls import path, include

#from . import views
#from .views import *
from .views.project_views import *
from .views.inquiry_views import *
from .views.purchase_order_views import *

app_name = "purchasing"

urlpatterns = [
    path('project_data/', ProjectDataView.as_view(), name="project_data"),
    path('project_add/', ProjectAddView.as_view(), name = "project_add"),
    path('project_update/<int:id>/', ProjectUpdateView.as_view(), name = "project_update"),
    path('project_delete/<str:list>/', ProjectDeleteView.as_view(), name = "project_delete"),
    
    path('project_item_add_type/p_<int:id>/', ProjectItemAddTypeView.as_view(), name = "project_item_add_type"),
    path('project_item_add/p_<int:id>/', ProjectItemAddView.as_view(), name = "project_item_add"),
    path('project_item_delete/<str:list>', ProjectItemDeleteView.as_view(), name = "project_item_delete"),
    
    path('inquiry_data/', InquiryDataView.as_view(), name="inquiry_data"),
    path('inquiry_add/p_<int:id>/', InquiryAddView.as_view(), name = "inquiry_add"),
    path('inquiry_update/<int:id>/', InquiryUpdateView.as_view(), name = "inquiry_update"),
    path('inquiry_delete/<str:list>/', InquiryDeleteView.as_view(), name = "inquiry_delete"),
    path('inquiry_pdf/<int:id>/', InquiryPdfView.as_view(), name = "inquiry_pdf"),
    path('inquiry_sent/<int:id>/', InquirySentView.as_view(), name = "inquiry_sent"),
    
    path('purchase_order_data/', PurchaseOrderDataView.as_view(), name="purchase_order_data"),
    path('purchase_order_add/i_<int:id>/', PurchaseOrderAddView.as_view(), name = "purchase_order_add"),
    path('purchase_order_update/<int:id>/', PurchaseOrderUpdateView.as_view(), name = "purchase_order_update"),
    path('purchase_order_delete/<str:list>/', PurchaseOrderDeleteView.as_view(), name = "purchase_order_delete"),
    path('purchase_order_pdf/<int:id>/', PurchaseOrderPdfView.as_view(), name = "purchase_order_pdf"),
    path('purchase_order_item_place/', PurchaseOrderItemPlaceView.as_view(), name = "purchase_order_item_place"),

    path('purchase_order_document/<int:id>/', PurchaseOrderDocumentView.as_view(), name = "purchase_order_document"),
    path('purchase_order_document_add/ot_<int:id>/', PurchaseOrderDocumentAddView.as_view(), name = "purchase_order_document_add"),
    path('purchase_order_document_delete/<int:id>/', PurchaseOrderDocumentDeleteView.as_view(), name = "purchase_order_document_delete"),
    path('purchase_order_document_pdf/<int:id>_<str:name>/', PurchaseOrderDocumentPdfView.as_view(), name = "purchase_order_document_pdf"),
    
    path('api/', include("purchasing.api.urls")),
]