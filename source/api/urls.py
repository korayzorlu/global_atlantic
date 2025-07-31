from django.urls import path, include
from rest_framework import routers

from source.api.views import *

router = routers.DefaultRouter()
router.register(r'companies', CompanyList, "companies_api")
router.register(r'banks', BankList, "banks_api")

urlpatterns = [
    path('',include(router.urls)),
]
