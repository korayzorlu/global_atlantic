from django.urls import path, include
from rest_framework import routers

from data.api.views import *

router = routers.DefaultRouter()
router.register(r'parts', PartList, "parts_api")
router.register(r'part_makers', PartMakerList, "part_makers_api")
router.register(r'part_types', PartTypeList, "part_types_api")
router.register(r'makers', MakerList, "makers_api")
router.register(r'maker_types', MakerTypeList, "maker_types_api")
router.register(r'maker_types_add', MakerTypeAddList, "maker_types_add_api")

urlpatterns = [
    path('',include(router.urls)),
    path('part_uniques', PartUniqueList.as_view(), name="part_uniques_api"),
    #path('parts', PartList.as_view(), name="parts_api"),
    path('parts_for_ts', PartForTechnicalSpecificationList.as_view(), name="parts_for_ts_api"),
    path('service_cards', ServiceCardList.as_view(), name="service_cards_api"),
    path('expenses', ExpenseList.as_view(), name="expenses_api"),
]
