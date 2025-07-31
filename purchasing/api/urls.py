from django.urls import path, include
from rest_framework import routers

from purchasing.api.views import *

router = routers.DefaultRouter()
router.register(r'projects', ProjectList, "projects_api")
router.register(r'project_items', ProjectItemList, "project_items_api")
router.register(r'inquiries', InquiryList, "inquiries_api")
router.register(r'inquiry_items', InquiryItemList, "inquiry_items_api")
router.register(r'purchase_orders', PurchaseOrderList, "purchase_orders_api")
router.register(r'purchase_order_items', PurchaseOrderItemList, "purchase_order_items_api")

urlpatterns = [
    path('',include(router.urls)),
]
