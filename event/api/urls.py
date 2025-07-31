from django.urls import path, include
from rest_framework import routers

from event.api.views import *

router = routers.DefaultRouter()
router.register(r'events', EventList, "events_api")

urlpatterns = [
    path('',include(router.urls)),
]
