from django.contrib import admin
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin
from pyheif_pillow_opener import register_heif_opener

from .models import *


register_heif_opener()

@admin.register(Acceptance)
class AcceptanceAdmin(admin.ModelAdmin):
    list_display = ["id", "acceptanceNo", "customer", "acceptanceDate", "created_date"]
    list_display_links = ["acceptanceNo"]
    search_fields = ["acceptanceNo"]
    list_filter = ["created_date"]
    inlines = []
    ordering = ["-created_date"]
    class Meta:
        model = Acceptance

@admin.register(AcceptanceEquipment)
class AcceptanceEquipmentAdmin(admin.ModelAdmin):
    list_display = ["id", "maker", "makerType", "category", "serialNo", "cyl", "description", "version"]
    list_display_links = ["serialNo"]
    search_fields = ["id", "equipment__maker__name", "equipment__makerType__type", "equipment__category", "equipment__serial", "equipment__cyl", "equipment__description", "equipment__version"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    
    def serialNo(self, obj):
        return obj.equipment.serialNo if obj.equipment else ''
    
    def maker(self, obj):
        return obj.equipment.maker.name if obj.equipment else ''
    
    def makerType(self, obj):
        return obj.equipment.makerType.type if obj.equipment else ''
    
    def category(self, obj):
        return obj.equipment.category if obj.equipment else ''
    
    def cyl(self, obj):
        return obj.equipment.cyl if obj.equipment else ''
    
    def description(self, obj):
        return obj.equipment.description if obj.equipment else ''
    
    def version(self, obj):
        return obj.equipment.version if obj.equipment else ''
    
    class Meta:
        model = AcceptanceEquipment

class OfferImageAdmin(admin.StackedInline):
    model = OfferImage

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ["id", "offerNo", "customer", "vessel", "person", "offerDate", "created_date"]
    list_display_links = ["offerNo"]
    search_fields = ["offerNo"]
    list_filter = ["created_date"]
    inlines = [OfferImageAdmin]
    ordering = ["-created_date"]
    class Meta:
        model = Offer

@admin.register(OfferServiceCard)
class OfferServiceCardAdmin(admin.ModelAdmin):
    list_display = ["id", "code", "name"]
    list_display_links = ["id"]
    search_fields = ["serviceCard__code", "serviceCard__name"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    
    def code(self, obj):
        return obj.serviceCard.code if obj.serviceCard else ""
    
    def name(self, obj):
        return obj.serviceCard.name if obj.serviceCard else ""
    class Meta:
        model = OfferServiceCard

admin.site.register(OfferExpense)
@admin.register(OfferPart)
class OfferPartAdmin(admin.ModelAdmin):
    list_display = ["id", "offer", "part", "quantity", "unitPrice", "totalPrice"]
    list_display_links = ["id"]
    search_fields = ["id"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    class Meta:
        model = OfferPart
admin.site.register(OfferImage)

@admin.register(OfferNote)
class OfferNoteAdmin(admin.ModelAdmin):
    list_display = ["id","user","offer", "title", "text","offerNoteDate"]
    list_display_links = ["id"]
    search_fields = ["user__first_name","user__last_name","offer__offerNo","title","text","offerNoteDate"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    
    def user(self, obj):
        return obj.user.first_name + " " + obj.user.last_name if obj.user else ""
    
    def offer(self, obj):
        return obj.offer.offerNo if obj.offer else ""
    class Meta:
        model = OfferNote
