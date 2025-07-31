from django.urls import path, include
from rest_framework import routers

from sale.api.views import *

router = routers.DefaultRouter()
router.register(r'projects', ProjectList, "projects_api")
router.register(r'requests', RequestList, "requests_api")
router.register(r'request_parts', RequestPartList, "request_parts_api")
router.register(r'inquiries', InquiryList, "inquiries_api")
router.register(r'inquiry_parts', InquiryPartList, "inquiry_parts_api")
router.register(r'quotations', QuotationList, "quotations_api")
router.register(r'quotation_parts', QuotationPartList, "quotation_parts_api")
router.register(r'quotation_extras', QuotationExtraList, "quotation_extras_api")
router.register(r'purchase_orders', PurchaseOrderList, "purchase_orders_api")
router.register(r'purchase_order_suppliers', PurchaseOrderSupplierList, "purchase_order_suppliers_api")
router.register(r'purchase_order_customers', PurchaseOrderCustomerList, "purchase_order_customers_api")
router.register(r'purchase_order_vessels', PurchaseOrderVesselList, "purchase_order_vessels_api")
router.register(r'order_confirmation_customers', OrderConfirmationCustomerList, "order_confirmation_customers_api")
router.register(r'quotation_customers', QuotationCustomerList, "quotation_customers_api")
router.register(r'purchase_order_parts', PurchaseOrderPartList, "purchase_order_parts_api")
router.register(r'order_trackings', OrderTrackingList, "order_trackings_api")
router.register(r'dispatch_orders', DispatchOrderList, "dispatch_orders_api")
router.register(r'dispatch_order_parts', DispatchOrderPartList, "dispatch_order_parts_api")

urlpatterns = [
    path('',include(router.urls)),
    path('order_confirmations', OrderConfirmationList.as_view(), name="order_confirmations_api"),
    path('order_not_confirmations', OrderNotConfirmationList.as_view(), name="order_not_confirmations_api"),
]
