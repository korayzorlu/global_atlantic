from django.urls import path, include
from rest_framework import routers

from note.api.views import *

router = routers.DefaultRouter()
router.register(r'notes', NoteList, "notes_api")

urlpatterns = [
    path('',include(router.urls)),
]
