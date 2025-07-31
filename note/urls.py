from django.urls import path, include

from . import views
from .views import *

app_name = "note"

urlpatterns = [
    path('note_dashboard_data/', NoteDashboardDataView.as_view(), name="note_dashboard_data"),
    path('note_add/', views.NoteAddView.as_view(), name = "note_add"),
    path('note_delete/', views.NoteDeleteView.as_view(), name = "note_delete"),
    path('note_update/<int:id>/', views.NoteUpdateView.as_view(), name = "note_update"),
    
    path('api/', include("note.api.urls")),
]
