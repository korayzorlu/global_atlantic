from django.contrib import admin

# Register your models here.
from parts.models import *

admin.site.register(Maker)
admin.site.register(MakerCategory)
admin.site.register(MakerDocument)
admin.site.register(MakerType)
admin.site.register(MakerTypeCategory)
admin.site.register(MakerTypeDocument)
admin.site.register(PartUnit)
admin.site.register(PartCategory)
admin.site.register(Part)
admin.site.register(PartImage)
admin.site.register(PartDocument)
admin.site.register(PartManufacturer)
admin.site.register(PartCompatibility)
admin.site.register(PartSupplier)
admin.site.register(RelatedSet)
admin.site.register(RelatedSetImage)
admin.site.register(RelatedSetDocument)
