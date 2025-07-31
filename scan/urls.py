from django.urls import path, include

from . import views
from .views import *

app_name = "scan"

urlpatterns = [
    path('vessel_api/', VesselApiDataView.as_view(), name="vessel_api"),
]
