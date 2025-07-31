from django.urls import path

from information.api.views import *

urlpatterns = [
    path('countries', CountryList.as_view(), name="countries_api"),
    path('cities', CityList.as_view(), name="cities_api"),
    path('companies', CompanyList.as_view(), name="companies_api"),
    path('companies/customers', CompanyCustomerList.as_view(), name="companies_customers_api"),
    path('companies/suppliers', CompanySupplierList.as_view(), name="companies_suppliers_api"),
    path('company/<int:pk>', CompanyAPI.as_view(), name="company_api"),
    path('contacts', ContactList.as_view(), name="contacts_api"),
    path('contact/<int:pk>', ContactAPI.as_view(), name="contact_api"),
    path('vessels', VesselList.as_view(), name="vessels_api"),
    path('vessel/<int:pk>', VesselAPI.as_view(), name="vessel_api"),

    path('vessel_info/vesselfinder/<int:imo>', VesselDataFromOuter.as_view(), name="vesselfinder_imo_api"),
]
