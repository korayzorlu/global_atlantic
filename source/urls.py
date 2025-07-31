from django.urls import path, include

from . import views
from .views import *

app_name = "source"

urlpatterns = [
    path('bank_data/', BankDataView.as_view(), name="bank_data"),
    path('bank_add/', views.BankAddView.as_view(), name = "bank_add"),
    path('bank_update/<int:id>/', views.BankUpdateView.as_view(), name = "bank_update"),
    
    path('api/', include("source.api.urls")),
]
