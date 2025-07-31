from django.urls import path, include

from .views import *

app_name = "parts"

urlpatterns = [
    path('maker_add/', MakerAddView.as_view(), name="maker_add"),
    path('maker/<int:maker_id>', MakerDetailView.as_view(), name="maker_detail"),
    path('maker_edit/<int:maker_id>', MakerEditView.as_view(), name="maker_edit"),
    path('maker_delete/<int:maker_id>', MakerDeleteView.as_view(), name="maker_delete"),
    path('maker_type_delete/<int:maker_type_id>', MakerTypeDeleteView.as_view(), name="maker_type_delete"),
    path('maker_document_delete/<int:maker_document_id>', MakerDocumentDeleteView.as_view(),
         name="maker_document_delete"),

    path('manufacturer_add/', ManufacturerAddView.as_view(), name="manufacturer_add"),
    path('manufacturer/<int:manufacturer_id>', ManufacturerDetailView.as_view(), name="manufacturer_detail"),
    path('manufacturer_edit/<int:manufacturer_id>', ManufacturerEditView.as_view(), name="manufacturer_edit"),
    path('manufacturer_delete/<int:manufacturer_id>', ManufacturerDeleteView.as_view(), name="manufacturer_delete"),

    path('part_add/', PartAddView.as_view(), name="part_add"),
    path('part/<int:part_id>', PartDetailView.as_view(), name="part_detail"),
    path('part_client/<uuid:part_uuid>', PartClientView.as_view(), name="part_client"),
    path('part_edit/<int:part_id>', PartEditView.as_view(), name="part_edit"),
    path('part_delete/<int:part_id>', PartDeleteView.as_view(), name="part_delete"),
    path('part_compatibility_delete/<int:part_compatibility_id>', PartCompatibilityDeleteView.as_view(),
         name="part_compatibility_delete"),
    path('part_supplier_delete/<int:part_supplier_id>', PartSupplierDeleteView.as_view(), name="part_supplier_delete"),
    path('part_manufacturer_delete/<int:part_manufacturer_id>', PartManufacturerDeleteView.as_view(),
         name="part_manufacturer_delete"),
    path('part_document_delete/<int:part_document_id>', PartDocumentDeleteView.as_view(),
         name="part_document_delete"),
    path('part_image_delete/<int:part_image_id>', PartImageDeleteView.as_view(), name="part_image_delete"),

    path('related_set_add/', RelatedSetAddView.as_view(), name="related_set_add"),
    path('related_set/<int:related_set_id>', RelatedSetDetailView.as_view(), name="related_set_detail"),
    path('related_set_client/<uuid:related_set_uuid>', RelatedSetClientView.as_view(), name="related_set_client"),
    path('related_set_edit/<int:related_set_id>', RelatedSetEditView.as_view(), name="related_set_edit"),
    path('related_set_delete/<int:related_set_id>', RelatedSetDeleteView.as_view(), name="related_set_delete"),
    path('related_set_document_delete/<int:related_set_document_id>', RelatedSetDocumentDeleteView.as_view(),
         name="related_set_document_delete"),
    path('related_set_image_delete/<int:related_set_image_id>', RelatedSetImageDeleteView.as_view(),
         name="related_set_image_delete"),

    path('api/', include("parts.api.urls")),
    path('maker_data/', MakerDataView.as_view(), name="maker_data"),
    path('manufacturer_data/', ManufacturerDataView.as_view(), name="manufacturer_data"),
    path('part_data/', PartDataView.as_view(), name="part_data"),
    path('related_set_data/', RelatedSetDataView.as_view(), name="related_set_data"),

]
