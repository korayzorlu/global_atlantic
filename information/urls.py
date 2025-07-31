from django.urls import path, include

from . import views
from .views import *

app_name = "information"

urlpatterns = [
    path('company_add/', CompanyAddView.as_view(), name="company_add"),
    path('company/<int:company_id>', CompanyDetailView.as_view(), name="company_detail"),
    path('company_edit/<int:company_id>', CompanyEditView.as_view(), name="company_edit"),
    path('company_delete/<int:company_id>', CompanyDeleteView.as_view(), name="company_delete"),

    path('contact_add/', ContactAddView.as_view(), name="contact_add"),
    path('contact/<int:contact_id>', ContactDetailView.as_view(), name="contact_detail"),
    path('contact_edit/<int:contact_id>', ContactEditView.as_view(), name="contact_edit"),
    path('contact_delete/<int:contact_id>', ContactDeleteView.as_view(), name="contact_delete"),
    path('contact_remove/<int:contact_id>/company/<int:company_id>', ContactRemoveView.as_view(),
         name="contact_remove"),

    path('vessel_add/', VesselAddView.as_view(), name="vessel_add"),
    path('vessel/<int:vessel_id>', VesselDetailView.as_view(), name="vessel_detail"),
    path('vessel_edit/<int:vessel_id>', VesselEditView.as_view(), name="vessel_edit"),
    path('vessel_delete/<int:vessel_id>', VesselDeleteView.as_view(), name="vessel_delete"),
    path('vessel_remove/<int:vessel_id>', VesselRemoveView.as_view(), name="vessel_remove"),

    path('customer_data/', CustomerDataView.as_view(), name="customer_data"),
    path('supplier_data/', SupplierDataView.as_view(), name="supplier_data"),
    path('vessel_data/', VesselDataView.as_view(), name="vessel_data"),
    path('contact_person_data/', ContactDataView.as_view(), name="contact_person_data"),

    path('api/', include("information.api.urls")),
]
