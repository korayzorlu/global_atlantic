from django.urls import path, include
from rest_framework import routers

from warehouse.api.views import *

router = routers.DefaultRouter()
router.register(r'warehouses', WarehouseList, "warehouses_api")
router.register(r'part_item_groups', PartItemGroupList, "part_item_groups_api")
router.register(r'part_items', PartItemList, "part_items_api")
router.register(r'dispatches', DispatchList, "dispatches_api")

urlpatterns = [
    path('',include(router.urls)),
]
