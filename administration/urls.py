from django.urls import path, include

#from . import views
#from .views import *
from .views.access_authorization_views import *
from .views.data_authorization_views import *
from .views.user_authorization_views import *
from .views.user_views import *
from .views.company_views import *

app_name = "administration"

urlpatterns = [
    path('access_authorization_data/', AccessAuthorizationDataView.as_view(), name="access_authorization_data"),
    path('access_authorization_add/', AccessAuthorizationAddView.as_view(), name = "access_authorization_add"),
    path('access_authorization_update/<int:id>/', AccessAuthorizationUpdateView.as_view(), name = "access_authorization_update"),
    path('access_authorization_delete/<str:list>/', AccessAuthorizationDeleteView.as_view(), name = "access_authorization_delete"),
    
    path('data_authorization_data/', DataAuthorizationDataView.as_view(), name="data_authorization_data"),
    path('data_authorization_add/', DataAuthorizationAddView.as_view(), name = "data_authorization_add"),
    path('data_authorization_update/<int:id>/', DataAuthorizationUpdateView.as_view(), name = "data_authorization_update"),
    path('data_authorization_delete/<str:list>/', DataAuthorizationDeleteView.as_view(), name = "data_authorization_delete"),
    
    path('user_authorization_data/', UserAuthorizationDataView.as_view(), name="user_authorization_data"),
    path('user_authorization_update/<int:id>/', UserAuthorizationUpdateView.as_view(), name = "user_authorization_update"),
    
    path('user_data/', UserDataView.as_view(), name="user_data"),
    path('user_add/', UserAddView.as_view(), name = "user_add"),
    path('user_update/<int:id>/', UserUpdateView.as_view(), name = "user_update"),
    path('user_delete/<str:list>/', UserDeleteView.as_view(), name = "user_delete"),
    
    path('user_source_company_add/u_<int:id>/', UserSourceCompanyAddView.as_view(), name = "user_source_company_add"),
    path('user_source_company_delete/u_<int:id>_list_<str:list>', UserSourceCompanyDeleteView.as_view(), name = "user_source_company_delete"),
    
    path('company_data/', CompanyDataView.as_view(), name="company_data"),
    path('company_add/', CompanyAddView.as_view(), name = "company_add"),
    path('company_update/<int:id>/', CompanyUpdateView.as_view(), name = "company_update"),
    path('company_delete/<str:list>/', CompanyDeleteView.as_view(), name = "company_delete"),
    
    path('api/', include("administration.api.urls")),
]