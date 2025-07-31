from django.urls import path, include
from rest_framework import routers

from card.api.views import *

router = routers.DefaultRouter()
#router.register(r'companies', CompanyList, "companies_api")
router.register(r'currents', CurrentList, "currents_api")
router.register(r'banks', BankList, "banks_api")
router.register(r'vessels', VesselList, "vessels_api")
router.register(r'engine_parts', EnginePartList, "engine_parts_api")
router.register(r'owners', OwnerList, "owners_api")
router.register(r'billing_in_vessels', BillingInVesselList, "billing_in_vessels_api")
router.register(r'billings', BillingList, "billings_api")
router.register(r'currencies', CurrencyList, "currencies_api")

urlpatterns = [
    path('',include(router.urls)),
    path('countries', CountryList.as_view(), name="countries_api"),
    path('cities', CityList.as_view(), name="cities_api"),
    path('companies', CompanyList.as_view(), name="companies_api"),
    path('persons', PersonList.as_view(), name="persons_api"),
    path('vessel_histories/<int:id>/', VesselHistoryList.as_view(), name="vessel_histories_api"),
]
