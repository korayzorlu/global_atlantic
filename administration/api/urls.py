from django.urls import path, include
from rest_framework import routers

from administration.api.views import *

router = routers.DefaultRouter()
router.register(r'access_authorizations', AccessAuthorizationList, "access_authorizations_api")
router.register(r'data_authorizations', DataAuthorizationList, "data_authorizations_api")
router.register(r'user_authorizations', UserAuthorizationList, "user_authorizations_api")
router.register(r'users', UserList, "users_api")
router.register(r'user_source_companies', UserSourceCompanyList, "user_source_companies_api")
router.register(r'companies', CompanyList, "companies_api")

urlpatterns = [
    path('',include(router.urls)),
]
