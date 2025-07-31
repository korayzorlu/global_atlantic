from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import *




@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "startDate", "endDate", "startTime", "endTime"]
    list_display_links = ["title"]
    search_fields = ["title"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-pk"]
    class Meta:
        model = Event