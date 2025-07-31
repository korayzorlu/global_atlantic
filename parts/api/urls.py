from django.urls import path

from parts.api.views import *

urlpatterns = [
    path('makers', MakerList.as_view(), name="makers_api"),
    path('maker/<int:pk>', MakerAPI.as_view(), name="maker_api"),
    path('maker_types', MakerTypeList.as_view(), name="maker_types_api"),
    path('maker_type/<int:pk>', MakerTypeAPI.as_view(), name="maker_type_api"),
    path('maker_document/<int:pk>', MakerDocumentAPI.as_view(), name="maker_document_api"),
    path('maker_type_document/<int:pk>', MakerTypeDocumentAPI.as_view(), name="maker_type_document_api"),

    path('manufacturers', ManufacturerList.as_view(), name="manufacturers_api"),
    path('manufacturer/<int:pk>', ManufacturerAPI.as_view(), name="manufacturer_api"),

    path('parts', PartList.as_view(), name="parts_api"),
    path('part/<int:pk>', PartAPI.as_view(), name="part_api"),
    path('part_compatibility/<int:pk>', PartCompatibilityAPI.as_view(), name="part_compatibility_api"),
    path('part_supplier/<int:pk>', PartSupplierAPI.as_view(), name="part_supplier_api"),
    path('part_manufacturer/<int:pk>', PartManufacturerAPI.as_view(), name="part_manufacturer_api"),
    path('part_image/<int:pk>', PartImageAPI.as_view(), name="part_image_api"),
    path('part_document/<int:pk>', PartDocumentAPI.as_view(), name="part_document_api"),

    path('related_sets', RelatedSetList.as_view(), name="related_sets_api"),
    path('related_set/<int:pk>', RelatedSetAPI.as_view(), name="related_set_api"),
    path('related_set_image/<int:pk>', RelatedSetImageAPI.as_view(), name="related_set_image"),
    path('related_set_document/<int:pk>', RelatedSetDocumentAPI.as_view(), name="related_set_document"),
]
