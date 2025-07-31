from rest_framework import serializers

from rest_framework.utils import html, model_meta, representation
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.contrib.auth.models import User

from warehouse.models import Warehouse,Item,ItemGroup,Dispatch

class WarehouseListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sourceCompany = serializers.SerializerMethodField()
    code = serializers.CharField()
    name = serializers.CharField()
    country = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    address = serializers.CharField()
    phone1 = serializers.CharField()
    
    def get_sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ''
    
    def get_country(self, obj):
        return obj.country.international_formal_name if obj.country else ''
    
    def get_city(self, obj):
        return obj.city.name if obj.city else ''

class ItemGroupListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sourceCompany = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    partUniqueCode = serializers.SerializerMethodField()
    partUnique = serializers.SerializerMethodField()
    name = serializers.CharField()
    category = serializers.CharField()
    unit = serializers.CharField()
    quantity = serializers.FloatField()
    
    def get_sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ''
    
    def get_maker(self, obj):
        return obj.part.maker.name if obj.part.maker else ''
    
    def get_type(self, obj):
        return obj.part.type.type if obj.part.type else ''
    
    def get_partUniqueCode(self, obj):
        return obj.part.partUniqueCode if obj.part else ''
    
    def get_partUnique(self, obj):
        return obj.part.partUnique.code if obj.part.partUnique else ''
    
    def get_items(self, obj):
        items = obj.item_item_group.select_related("warehouse","currency").all().order_by("itemDate")  # ManyToManyField'dan tüm ilişkili nesneleri al
        items_list = []
        for item in items:
            if item.incomingInvoiceItem:
                invoice = item.incomingInvoiceItem.invoice.incomingInvoiceNo
                if invoice:
                    invoice = invoice
                else:
                    invoice = ""
            else:
                invoice = ""

            items_list.append({
                "id": item.id,
                "itemNo": item.itemNo,
                "unit" : item.unit,
                "quantity" : item.quantity,
                "warehouse" : item.warehouse.name,
                "location" : item.location,
                "buyingPrice" : item.buyingPrice,
                "cost" : item.cost,
                "salePrice" : item.salePrice,
                "currency" : item.currency.code,
                "vat" : item.vat,
                "weight" : item.weight,
                "width" : item.width,
                "height" : item.height,
                "itemDate" : item.itemDate.strftime("%d.%m.%Y"),
                "invoice" : invoice
            })
        return items_list
   
class ItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sourceCompany = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    partUniqueCode = serializers.SerializerMethodField()
    partUnique = serializers.SerializerMethodField()
    invoice = serializers.SerializerMethodField()
    itemNo = serializers.CharField()
    itemDate = serializers.DateField()
    name = serializers.CharField()
    location = serializers.CharField()
    category = serializers.CharField()
    unit = serializers.CharField()
    quantity = serializers.FloatField()
    
    def get_sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ''
    
    def get_maker(self, obj):
        return obj.part.maker.name if obj.part.maker else ''
    
    def get_type(self, obj):
        return obj.part.type.type if obj.part.type else ''
    
    def get_partUniqueCode(self, obj):
        return obj.part.partUniqueCode if obj.part else ''
    
    def get_partUnique(self, obj):
        return obj.part.partUnique.code if obj.part.partUnique else ''
    
    def get_invoice(self, obj):
        return obj.incomingInvoiceItem.invoice.invoiceNo if obj.incomingInvoiceItem else ''
    
class DispatchListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sourceCompany = serializers.SerializerMethodField()
    dispatchNo = serializers.CharField()

    def get_sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ''