from django.urls import path, include

from . import views
from .views import *

app_name = "event"

urlpatterns = [
    path('calendar_data/', CalendarDataView.as_view(), name="calendar_data"),
    
    path('event_add/', views.EventAddView.as_view(), name = "event_add"),
    path('event_update/', views.EventUpdateView.as_view(), name = "event_update"),
    path('event_delete/', views.EventDeleteView.as_view(), name = "event_delete"),
    
    path('api/', include("event.api.urls")),
]
