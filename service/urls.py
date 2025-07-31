from django.urls import path, include

from .views.acceptance_views import *
from .views.offer_views import *
from .views.active_project_views import *
from .views.finish_project_views import *

app_name = "service"

urlpatterns = [
    path('acceptance_data/', AcceptanceDataView.as_view(), name="acceptance_data"),
    path('acceptance_add/', AcceptanceAddView.as_view(), name = "acceptance_add"),
    path('acceptance_update/<int:id>/', AcceptanceUpdateView.as_view(), name = "acceptance_update"),
    path('acceptance_delete/<str:list>/', AcceptanceDeleteView.as_view(), name = "acceptance_delete"),
    path('acceptance_pdf/<int:id>/', AcceptancePdfView.as_view(), name = "acceptance_pdf"),
    
    path('acceptance_service_card_add_in_detail/o_<int:id>/', AcceptanceServiceCardInDetailAddView.as_view(), name = "acceptance_service_card_add_in_detail"),
    path('acceptance_service_card_delete/<str:list>', AcceptanceServiceCardDeleteView.as_view(), name = "acceptance_service_card_delete"),
    
    path('offer_data/', OfferDataView.as_view(), name="offer_data"),
    path('offer_add/', OfferAddView.as_view(), name = "offer_add"),
    path('offer_update/<int:id>/', OfferUpdateView.as_view(), name = "offer_update"),
    path('offer_delete/<str:list>/', OfferDeleteView.as_view(), name = "offer_delete"),
    path('offer_pdf/<int:id>/', OfferPdfView.as_view(), name = "offer_pdf"),
    
    path('offer_service_card_add_in_detail/o_<int:id>/', OfferServiceCardInDetailAddView.as_view(), name = "offer_service_card_add_in_detail"),
    path('offer_service_card_delete/<str:list>', OfferServiceCardDeleteView.as_view(), name = "offer_service_card_delete"),
    
    path('active_project_data/', ActiveProjectDataView.as_view(), name="active_project_data"),
    path('active_project_add/a_<int:id>/', ActiveProjectAddView.as_view(), name = "active_project_add"),
    path('active_project_update/<int:id>/', ActiveProjectUpdateView.as_view(), name = "active_project_update"),
    path('active_project_delete/<str:list>', ActiveProjectDeleteView.as_view(), name = "active_project_delete"),
    path('active_project_pdf/<int:id>_type_<str:type>/', ActiveProjectPdfView.as_view(), name = "active_project_pdf"),
    
    path('active_project_service_card_add_in_detail/o_<int:id>/', ActiveProjectServiceCardInDetailAddView.as_view(), name = "active_project_service_card_add_in_detail"),
    path('active_project_service_card_extra_add_in_detail/o_<int:id>/', ActiveProjectServiceCardExtraInDetailAddView.as_view(), name = "active_project_service_card_extra_add_in_detail"),
    
    path('active_project_expense_add_in_detail/o_<int:id>/', ActiveProjectExpenseInDetailAddView.as_view(), name = "active_project_expense_add_in_detail"),
    path('active_project_expense_delete/<str:list>', ActiveProjectExpenseDeleteView.as_view(), name = "active_project_expense_delete"),
    
    path('active_project_part_add_in_detail/o_<int:id>/', ActiveProjectPartInDetailAddView.as_view(), name = "active_project_part_add_in_detail"),
    path('active_project_part_delete/<str:list>', ActiveProjectPartDeleteView.as_view(), name = "active_project_part_delete"),
    
    path('active_project_image/<int:id>/', ActiveProjectImageView.as_view(), name = "active_project_image"),
    path('active_project_image_add/o_<int:id>/', ActiveProjectImageAddView.as_view(), name = "active_project_image_add"),
    path('active_project_image_delete/<int:id>/', ActiveProjectImageDeleteView.as_view(), name = "active_project_image_delete"),

    path('active_project_document/<int:id>/', ActiveProjectDocumentView.as_view(), name = "active_project_document"),
    path('active_project_document_add/ot_<int:id>/', ActiveProjectDocumentAddView.as_view(), name = "active_project_document_add"),
    path('active_project_document_delete/<int:id>/', ActiveProjectDocumentDeleteView.as_view(), name = "active_project_document_delete"),
    path('active_project_document_pdf/<int:id>_<str:name>/', ActiveProjectDocumentPdfView.as_view(), name = "active_project_document_pdf"),
    
    path('active_project_note_add/o_<int:id>/', ActiveProjectNoteAddView.as_view(), name = "active_project_note_add"),
    path('active_project_note_delete/', ActiveProjectNoteDeleteView.as_view(), name = "active_project_note_delete"),
    
    path('finish_project_data/', FinishProjectDataView.as_view(), name="finish_project_data"),
    path('finish_project_update/<int:id>/', FinishProjectUpdateView.as_view(), name = "finish_project_update"),
    path('finish_project_pdf/<int:id>_type_<str:type>/', FinishProjectPdfView.as_view(), name = "finish_project_pdf"),

    path('finish_project_image/<int:id>/', FinishProjectImageView.as_view(), name = "finish_project_image"),
    path('finish_project_image_add/o_<int:id>/', FinishProjectImageAddView.as_view(), name = "finish_project_image_add"),
    path('finish_project_image_delete/<int:id>/', FinishProjectImageDeleteView.as_view(), name = "finish_project_image_delete"),

    path('finish_project_document/<int:id>/', FinishProjectDocumentView.as_view(), name = "finish_project_document"),
    path('finish_project_document_add/ot_<int:id>/', FinishProjectDocumentAddView.as_view(), name = "finish_project_document_add"),
    path('finish_project_document_delete/<int:id>/', FinishProjectDocumentDeleteView.as_view(), name = "finish_project_document_delete"),
    path('finish_project_document_pdf/<int:id>_<str:name>/', FinishProjectDocumentPdfView.as_view(), name = "finish_project_document_pdf"),

    path('finish_project_note_add/o_<int:id>/', FinishProjectNoteAddView.as_view(), name = "finish_project_note_add"),
    path('finish_project_note_delete/', FinishProjectNoteDeleteView.as_view(), name = "finish_project_note_delete"),
    
    path('api/', include("service.api.urls")),
]
