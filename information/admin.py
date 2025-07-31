from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from information.models import *

admin.site.register(Country)
admin.site.register(City)
admin.site.register(Company)
admin.site.register(CompanyGroup)
admin.site.register(Contact)
admin.site.register(ContactCompanyHistory)
admin.site.register(Vessel, SimpleHistoryAdmin)
# admin.site.register(VesselEngine)
# admin.site.register(VesselBilling)
# admin.site.register(VesselBillingDefault)
# admin.site.register(VesselDefaultPIC)
# admin.site.register(CompanyNote)
