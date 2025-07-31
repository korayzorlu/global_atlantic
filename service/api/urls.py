from django.urls import path, include
from rest_framework import routers

from service.api.views import *

router = routers.DefaultRouter()
router.register(r'acceptances', AcceptanceList, "acceptances_api")
router.register(r'acceptance_service_cards', AcceptanceServiceCardList, "acceptance_service_cards_api")
router.register(r'offers', OfferList, "offers_api")
router.register(r'offer_service_cards', OfferServiceCardList, "offer_service_cards_api")
router.register(r'offer_expenses', OfferExpenseList, "offer_expenses_api")
router.register(r'offer_parts', OfferPartList, "offer_parts_api")
router.register(r'offer_notes', OfferNoteList, "offer_notes_api")

urlpatterns = [
    path('',include(router.urls)),
]
