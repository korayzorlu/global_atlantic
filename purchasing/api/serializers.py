from rest_framework import serializers

from rest_framework.utils import html, model_meta, representation
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.contrib.auth.models import User

from purchasing.models import Project,ProjectItem,Inquiry,InquiryItem,PurchaseOrder,PurchaseOrderItem
from card.api.serializers import CompanyListSerializer
from user.api.serializers import UserListSerializer

class ProjectListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectCreator = serializers.SerializerMethodField()
    stage = serializers.CharField()
    supplier = serializers.SerializerMethodField()
    identificationCode = serializers.CharField()
    yearCode = serializers.CharField()
    code = serializers.CharField()
    projectNo = serializers.CharField()
    projectDate = serializers.DateField()
    customerRef = serializers.CharField()
    
    def get_projectCreator(self, obj):
        return obj.user.first_name + " " + obj.user.last_name if obj.user else ''
    
    def get_supplier(self, obj):
        return obj.supplier.name if obj.supplier else ''

class ProjectItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField()
    unit = serializers.CharField()
    sequency = serializers.IntegerField()
    quantity = serializers.FloatField()
    trDescription = serializers.CharField(allow_blank=True)
    startDate = serializers.DateField()
    endDate = serializers.DateField()
    
    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance
    
class InquiryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    projectCreator = serializers.SerializerMethodField()
    projectStage = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    identificationCode = serializers.CharField()
    yearCode = serializers.CharField()
    code = serializers.CharField()
    inquiryNo = serializers.CharField()
    supplierRef = serializers.CharField()
    inquiryDate = serializers.DateField()
    sessionKey = serializers.CharField()
    totalTotalPrice = serializers.FloatField()
    
    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def get_projectNo(self, obj):
        return obj.project.projectNo if obj.project else ''
    
    def get_projectCreator(self, obj):
        return obj.project.user.first_name + " " + obj.project.user.last_name if obj.project.user else ''
    
    def get_projectStage(self, obj):
        return obj.project.stage if obj.project else ''
    
    def get_supplier(self, obj):
        return obj.supplier.name if obj.supplier else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
    
class InquiryItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    unit = serializers.CharField()
    sessionKey = serializers.CharField()
    quantity = serializers.FloatField()
    sequency = serializers.IntegerField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    availability = serializers.IntegerField()
    availabilityType = serializers.CharField()
    itemDetails = serializers.SerializerMethodField()
    note = serializers.CharField(allow_blank=True)
    remark = serializers.CharField(allow_blank=True)
    
    # def get_name(self, obj):
    #     return obj.projectItem.name if obj.projectItem else ''
    
    # def get_description(self, obj):
    #     return obj.projectItem.description if obj.projectItem else ''
    
    # def get_unit(self, obj):
    #     return obj.projectItem.unit if obj.projectItem else ''
    
    def get_currency(self, obj):
        return obj.inquiry.currency.symbol if obj.inquiry.currency else ''
    
    def get_itemDetails(self, obj):
        inquiryItemsList = []
        inquiryItems = InquiryItem.objects.select_related("inquiry","inquiry__currency").filter(projectItem = obj.projectItem).exclude(id = obj.id).order_by("-id")
        
        for index, inquiryItem in enumerate(inquiryItems):
            inquiryItemsList.append({"date":inquiryItem.inquiry.inquiryDate.strftime("%d.%m.%Y"),"inquiry":inquiryItem.inquiry.inquiryNo,"unitPrice":round(inquiryItem.unitPrice,2),"currency":inquiryItem.inquiry.currency.symbol})
            if index == 2:
                break
            
        return {
            "lastItems" : inquiryItemsList
        }
    
    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance
    
class PurchaseOrderListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    projectCreator = serializers.SerializerMethodField()
    projectStage = serializers.SerializerMethodField()
    supplierId = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    supplierRef = serializers.SerializerMethodField()
    customerRef = serializers.SerializerMethodField()
    purchaseOrderNo = serializers.CharField()
    purchaseOrderDate = serializers.DateField()
    totalTotalPrice = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    invoiced = serializers.BooleanField()
    created_date = serializers.DateTimeField(format="%d.%m.%Y", required=False, read_only=True)
    
    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def get_projectNo(self, obj):
        return obj.project.projectNo if obj.project else ''
    
    def get_projectCreator(self, obj):
        return obj.project.user.first_name + " " + obj.project.user.last_name if obj.project.user else ''
    
    def get_projectStage(self, obj):
        return obj.project.stage if obj.project else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
    
    def get_supplierId(self, obj):
        return obj.inquiry.supplier.id if obj.inquiry.supplier else ''
    
    def get_supplier(self, obj):
        return obj.inquiry.supplier.name if obj.inquiry.supplier else ''
    
    def get_supplierRef(self, obj):
        return obj.inquiry.supplierRef if obj.inquiry else ''
    
    def get_customerRef(self, obj):
        return obj.inquiry.project.customerRef if obj.inquiry else ''
    
class PurchaseOrderItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    purchaseOrderId = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    quantity = serializers.FloatField()
    sequency = serializers.IntegerField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    availability = serializers.CharField()
    availabilityType = serializers.CharField()
    quality = serializers.CharField()
    note = serializers.CharField(allow_blank=True)
    remark = serializers.CharField(allow_blank=True)
    placed = serializers.BooleanField()
    
    def get_purchaseOrderId(self, obj):
        return obj.purchaseOrder.id if obj.purchaseOrder else ''
    
    def get_name(self, obj):
        return obj.inquiryItem.projectItem.name if obj.inquiryItem.projectItem else ''
    
    def get_description(self, obj):
        return obj.inquiryItem.projectItem.description if obj.inquiryItem.projectItem else ''
    
    def get_unit(self, obj):
        return obj.inquiryItem.projectItem.unit if obj.inquiryItem.projectItem else ''
    
    def get_currency(self, obj):
        return obj.purchaseOrder.currency.symbol if obj.purchaseOrder.currency else ''
    
    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance