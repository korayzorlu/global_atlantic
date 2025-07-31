from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import *

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ["id","user","action","modelName", "objectId","objectName", "actionLogDate"]
    list_display_links = ["objectName"]
    search_fields = ["user__username","action","modelName","objectId","objectName","actionLogDate"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    autocomplete_fields = ["user"]
    
    def user(self, obj):
        return obj.user.username if obj.user else ""

    class Meta:
        model = ActionLog