from django.urls import path, include

from . import views

from .views.company_views import *
from .views.vessel_views import *
from .views.billing_views import *

app_name = "card"

urlpatterns = [
    path('card_data/', CardDataView.as_view(), name="card_data"),
    path('vessel_data/', VesselDataView.as_view(), name="vessel_data"),
    
    path('company_add/', CompanyAddView.as_view(), name = "company_add"),
    path('company_update/<int:id>/', CompanyUpdateView.as_view(), name = "company_update"),
    path('company_delete/<str:list>/', CompanyDeleteView.as_view(), name = "company_delete"),
    path('company_filter_excel/', CompanyFilterExcelView.as_view(), name = "company_filter_excel"),
    path('company_export_excel', CompanyExportExcelView.as_view(), name = "company_export_excel"),
    path('company_download_excel/', CompanyDownloadExcelView.as_view(), name = "company_download_excel"),
    path('get_updates_from_mikro/c_<int:id>_hk_<str:hesapKodu>/', CompanyUpdateFromMikroView.as_view(), name = "get_updates_from_mikro"),
    path('send_updates_to_mikro/c_<int:id>_hk_<str:hesapKodu>/', CompanyUpdateToMikroView.as_view(), name = "send_updates_to_mikro"),
    path('match_with_mikro/c_<int:id>_hk_<str:hesapKodu>/', CompanyMatchWithMikroView.as_view(), name = "match_with_mikro"),
    path('unmatch_with_mikro/c_<int:id>/', CompanyUnmatchWithMikroView.as_view(), name = "unmatch_with_mikro"),
    path('company_create_mikro/c_<int:id>_hk_<str:hesapKodu>/', CompanyCreateMikroView.as_view(), name = "company_create_mikro"),
    
    path('vessel_add/', VesselAddView.as_view(), name = "vessel_add"),
    path('vessel_update/<int:id>/', VesselUpdateView.as_view(), name = "vessel_update"),
    path('vessel_update_modal/<int:id>/', VesselUpdateModalView.as_view(), name = "vessel_update_modal"),
    path('vessel_delete/<str:list>/', VesselDeleteView.as_view(), name = "vessel_delete"),
    
    path('engine_part_add_in_detail/v_<int:id>/', EnginePartInDetailAddView.as_view(), name = "engine_part_add_in_detail"),
    path('engine_part_delete/<str:list>', EnginePartDeleteView.as_view(), name = "engine_part_delete"),
    
    path('person_add_in_company/', PersonAddInCompanyView.as_view(), name = "person_add_in_company"),
    path('person_add_in_vessel/', PersonAddInVesselView.as_view(), name = "person_add_in_vessel"),
    path('person_add_in_detail_vessel/', PersonInDetailVesselAddView.as_view(), name = "person_add_in_detail_vessel"),
    path('person_add_in_detail_company/', PersonInDetailCompanyAddView.as_view(), name = "person_add_in_detail_company"),
    path('person_update_in_vessel/<int:id>/', PersonUpdateInVesselView.as_view(), name = "person_update_in_vessel"),
    path('person_update_in_company/<int:id>/', PersonUpdateInCompanyView.as_view(), name = "person_update_in_company"),
    path('person_delete/<str:list>', PersonDeleteView.as_view(), name = "person_delete"),
    
    path('bank_add_in_detail_company/c_<int:id>/', BankInDetailCompanyAddView.as_view(), name = "bank_add_in_detail_company"),
    path('bank_update_in_company/<int:id>/', BankUpdateInCompanyView.as_view(), name = "bank_update_in_company"),
    path('bank_delete/<str:list>', BankDeleteView.as_view(), name = "bank_delete"),
    
    path('owner_add_in_vessel/', OwnerAddView.as_view(), name = "owner_add_in_vessel"),
    path('owner_add_in_detail/v_<int:id>/', OwnerInDetailAddView.as_view(), name = "owner_add_in_detail"),
    path('owner_delete/<str:list>', OwnerDeleteView.as_view(), name = "owner_delete"),
    
    path('billing_data/', BillingDataView.as_view(), name="billing_data"),
    path('billing_update/<int:id>/', BillingUpdateView.as_view(), name = "billing_update"),
    path('billing_add_in_detail/v_<int:id>/', BillingInDetailAddView.as_view(), name = "billing_add_in_detail"),
    path('billing_delete/<str:list>', BillingDeleteView.as_view(), name = "billing_delete"),
    path('billing_match_with_mikro/b_<int:id>_hk_<str:hesapKodu>/', BillingMatchWithMikroView.as_view(), name = "billing_match_with_mikro"),
    path('billing_unmatch_with_mikro/b_<int:id>/', BillingUnmatchWithMikroView.as_view(), name = "billing_unmatch_with_mikro"),
    path('billing_get_updates_from_mikro/c_<int:id>_hk_<str:hesapKodu>/', BillingUpdateFromMikroView.as_view(), name = "billing_get_updates_from_mikro"),
    path('billing_send_updates_to_mikro/c_<int:id>_hk_<str:hesapKodu>/', BillingUpdateToMikroView.as_view(), name = "billing_send_updates_to_mikro"),
    path('billing_create_mikro/c_<int:id>_hk_<str:hesapKodu>/', BillingCreateMikroView.as_view(), name = "billing_create_mikro"),
    
    path('company_logo/<int:id>/', CompanyLogoView.as_view(), name = "company-logo"),
    path('get-cities/', get_cities, name = "get-cities"),
    
    path('api/', include("card.api.urls")),
]
