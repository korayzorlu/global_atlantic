from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User




# Register your models here.
from user.models import *


class CustomCurrency(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at',)


class RecordAdmin(admin.ModelAdmin):
    list_display = ["username", "path", "response_code", "method", "created_at"]

admin.site.register(Notification)
admin.site.register(EmployeeType)
admin.site.register(Profile)
admin.site.register(Team)
admin.site.register(Education)

admin.site.register(Department)
admin.site.register(Position)
admin.site.register(Currency, CustomCurrency)
admin.site.register(Record, RecordAdmin)
admin.site.register(Certification)
