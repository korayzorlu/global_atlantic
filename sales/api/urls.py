from django.urls import path

from sales.api.views import *

urlpatterns = [
    path('project', ProjectCreateAPI.as_view(), name="project_create_api"),
    path('project/<int:pk>/update', ProjectUpdateAPI.as_view(), name="project_update_api"),
    path('project/<int:pk>', ProjectDetailAPI.as_view(), name="project_api"),
    path('projects', ProjectList.as_view(), name="projects_api"),
    path('project/duplicate/<int:pk>', ProjectDuplicateAPI.as_view(), name="project_duplicate_api"),
    
    path('projects_not_confirmed', ProjecNotConfirmedtList.as_view(), name="projects_not_confirmed_api"),
    path('projects_claims_follow_up', ProjectClaimsFollowUpList.as_view(), name="projects_claims_follow_up_api"),

    path('project_document', ProjectDocumentCreateAPI.as_view(), name="project_document_create_api"),
    path('project_document/<int:pk>/update', ProjectDocumentUpdateAPI.as_view(), name="project_document_update_api"),
    path('project_documents', ProjectDocumentList.as_view(), name="project_documents_api"),

    path('request', RequestCreateAPI.as_view(), name="request_create_api"),
    path('request/<int:pk>/update', RequestUpdateAPI.as_view(), name="request_update_api"),
    path('request/<int:pk>', RequestDetailAPI.as_view(), name="request_api"),
    path('requests', RequestList.as_view(), name="requests_api"),

    path('request_part', RequestPartCreateAPI.as_view(), name="request_part_create_api"),
    path('request_part/<int:pk>/update', RequestPartUpdateAPI.as_view(), name="request_part_update_api"),
    path('request_part/<int:pk>', RequestPartDetailAPI.as_view(), name="request_part_api"),
    path('request_parts', RequestPartList.as_view(), name="request_parts_api"),

    path('inquiry', InquiryCreateAPI.as_view(), name="inquiry_create_api"),
    path('inquiry/<int:pk>/update', InquiryUpdateAPI.as_view(), name="inquiry_update_api"),
    path('inquiry/<int:pk>', InquiryDetailAPI.as_view(), name="inquiry_api"),
    path('inquiries', InquiryList.as_view(), name="inquiries_api"),

    path('inquiry_part', InquiryPartCreateAPI.as_view(), name="inquiry_part_create_api"),
    path('inquiry_part/<int:pk>/update', InquiryPartUpdateAPI.as_view(), name="inquiry_part_update_api"),
    path('inquiry_part/<int:pk>', InquiryPartDetailAPI.as_view(), name="inquiry_part_api"),
    path('inquiry_parts', InquiryPartList.as_view(), name="inquiry_parts_api"),
    path('inquiry_add_parts/<int:pk>', InquiryPartAddList.as_view(), name="inquiry_add_parts_api"),

    path('quotation', QuotationCreateAPI.as_view(), name="quotation_create_api"),
    path('quotation/<int:pk>/update', QuotationUpdateAPI.as_view(), name="quotation_update_api"),
    path('quotation/<int:pk>', QuotationDetailAPI.as_view(), name="quotation_api"),
    path('quotations', QuotationList.as_view(), name="quotations_api"),

    path('quotation_part', QuotationPartCreateAPI.as_view(), name="quotation_part_create_api"),
    path('quotation_part_bulk', QuotationPartBulkCreateAPI.as_view(), name="quotation_part_bulk_create_api"),
    path('quotation_part/<int:pk>/update', QuotationPartUpdateAPI.as_view(), name="quotation_part_update_api"),
    path('quotation_part_bulk/<int:pk>/delete', QuotationPartBulkDeleteAPI.as_view(), name="quotation_part_bulk_delete_api"),
    path('quotation_part/<int:pk>', QuotationPartDetailAPI.as_view(), name="quotation_part_api"),
    path('quotation_parts', QuotationPartList.as_view(), name="quotation_parts_api"),

    path('order_confirmation', OrderConfirmationCreateAPI.as_view(), name="order_confirmation_create_api"),
    path('order_confirmation/<int:pk>/update', OrderConfirmationUpdateAPI.as_view(),
         name="order_confirmation_update_api"),
    path('order_confirmation/<int:pk>', OrderConfirmationDetailAPI.as_view(), name="order_confirmation_api"),
    path('order_confirmations', OrderConfirmationList.as_view(), name="order_confirmations_api"),
    
    path('order_not_confirmation', OrderNotConfirmationCreateAPI.as_view(), name="order_not_confirmation_create_api"),


    path('purchase_order', PurchaseOrderCreateAPI.as_view(), name="purchase_order_create_api"),
    path('purchase_order/<int:pk>/update', PurchaseOrderUpdateAPI.as_view(), name="purchase_order_update_api"),
    path('purchase_order/<int:pk>', PurchaseOrderDetailAPI.as_view(), name="purchase_order_api"),
    path('purchase_orders', PurchaseOrderList.as_view(), name="purchase_orders_api"),

    path('purchase_order_part', PurchaseOrderPartCreateAPI.as_view(), name="purchase_order_part_create_api"),
    path('purchase_order_part_list', PurchaseOrderPartListCreateAPI.as_view(),
         name="purchase_order_part_list_create_api"),
    path('purchase_order_part/<int:pk>/update', PurchaseOrderPartUpdateAPI.as_view(),
         name="purchase_order_part_update_api"),
    path('purchase_order_part/<int:pk>', PurchaseOrderPartDetailAPI.as_view(), name="purchase_order_part_api"),
    path('purchase_order_parts', PurchaseOrderPartList.as_view(), name="purchase_order_parts_api"),

    path('delivery', DeliveryCreateAPI.as_view(), name="delivery_create_api"),
    path('delivery/<int:pk>/update', DeliveryUpdateAPI.as_view(), name="delivery_update_api"),
    path('delivery/<int:pk>', DeliveryDetailAPI.as_view(), name="delivery_api"),
    path('deliveries', DeliveryList.as_view(), name="deliveries_api"),

    path('delivery/part', DeliveryPartAddAPI.as_view(), name="delivery_part_add_api"),
    path('delivery/<int:delivery_pk>/part/<int:delivery_part_pk>', DeliveryPartRemoveAPI.as_view(),
         name="delivery_part_remove_api"),

    path('delivery_transportation', DeliveryTransportationCreateAPI.as_view(),
         name="delivery_transportation_create_api"),
    path('delivery_transportation/<int:pk>/update', DeliveryTransportationUpdateAPI.as_view(),
         name="delivery_transportation_update_api"),
    path('delivery_transportation/<int:pk>', DeliveryTransportationDetailAPI.as_view(),
         name="delivery_transportation_api"),

    path('delivery_tax', DeliveryTaxCreateAPI.as_view(), name="delivery_tax_create_api"),
    path('delivery_tax/<int:pk>/update', DeliveryTaxUpdateAPI.as_view(), name="delivery_tax_update_api"),
    path('delivery_tax/<int:pk>', DeliveryTaxDetailAPI.as_view(), name="delivery_tax_api"),

    path('delivery_insurance', DeliveryInsuranceCreateAPI.as_view(), name="delivery_insurance_create_api"),
    path('delivery_insurance/<int:pk>/update', DeliveryInsuranceUpdateAPI.as_view(),
         name="delivery_insurance_update_api"),
    path('delivery_insurance/<int:pk>', DeliveryInsuranceDetailAPI.as_view(), name="delivery_insurance_api"),

    path('delivery_customs', DeliveryCustomsCreateAPI.as_view(), name="delivery_customs_create_api"),
    path('delivery_customs/<int:pk>/update', DeliveryCustomsUpdateAPI.as_view(), name="delivery_customs_update_api"),
    path('delivery_customs/<int:pk>', DeliveryCustomsDetailAPI.as_view(), name="delivery_customs_api"),

    path('delivery_packing', DeliveryPackingCreateAPI.as_view(), name="delivery_packing_create_api"),
    path('delivery_packing/<int:pk>/update', DeliveryPackingUpdateAPI.as_view(), name="delivery_packing_update_api"),
    path('delivery_packing/<int:pk>', DeliveryPackingDetailAPI.as_view(), name="delivery_packing_api"),

    path('claims_follow_up', ClaimsFollowUpCreateAPI.as_view(), name="claims_follow_up_create_api"),
    path('claims_follow_up/<int:pk>/update', ClaimsFollowUpUpdateAPI.as_view(), name="claims_follow_up_update_api"),
    path('claims_follow_up/<int:pk>', ClaimsFollowUpDetailAPI.as_view(), name="claims_follow_up_claims_follow_up_api"),

]
