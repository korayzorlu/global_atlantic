from rest_framework import serializers

from rest_framework.utils import html, model_meta, representation
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from sale.models import *
from django.contrib.auth.models import User

from card.api.serializers import CompanyListSerializer, VesselListSerializer, PersonListSerializer, CurrencyListSerializer
from data.api.serializers import MakerListSerializer, MakerTypeListSerializer, PartListSerializer
from user.api.serializers import UserListSerializer

import cProfile

def updateDetail(user,message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'private_' + str(user.id),
        {
            "type": "update_detail",
            "message": message,
            "location" : location
        }
    )
  
class ProjectListSerializer2(serializers.ModelSerializer):
    user = UserListSerializer()
    
    class Meta:
        model = Project
        fields = ["id", "projectNo", "user", "stage", "created_date"]

class ProjectListSerializer(serializers.Serializer):
    user = UserListSerializer()
    id = serializers.CharField()
    projectNo = serializers.CharField()
    stage = serializers.CharField()
    created_date = serializers.DateTimeField()
    
class RequestListSerializer2(serializers.ModelSerializer):
    project = ProjectListSerializer()
    customer = CompanyListSerializer()
    person = PersonListSerializer()
    vessel = VesselListSerializer()
    maker = MakerListSerializer()
    makerType = MakerTypeListSerializer()
    
    def to_internal_value(self, data):
        return Request.objects.get(pk=data['project']['id'])
    
    class Meta:
        model = Request
        fields = ["project", "identificationCode", "yearCode", "code", "requestNo", "customer", "person", "vessel", "requestDate", "customerRef", "maker", "makerType"]

class RequestListSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    projectCreator = serializers.SerializerMethodField()
    projectStage = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    person = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    makerType = serializers.SerializerMethodField()
    identificationCode = serializers.CharField()
    yearCode = serializers.CharField()
    code = serializers.CharField()
    requestNo = serializers.CharField()
    requestDate = serializers.DateField()
    customerRef = serializers.CharField()
    note = serializers.CharField()
    
    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def get_projectCreator(self, obj):
        return obj.project.user.first_name + " " + obj.project.user.last_name if obj.project.user else ''
    
    def get_projectStage(self, obj):
        return obj.project.stage if obj.project else ''
    
    def get_customer(self, obj):
        return obj.customer.name if obj.customer else ''
    
    def get_person(self, obj):
        person = ""
        if obj.person:
            person += obj.person.name
            if obj.vesselPerson:
                person += f" / {obj.vesselPerson.name}"
        else:
            if obj.vesselPerson:
                person += obj.vesselPerson.name

        return person
    
    def get_vessel(self, obj):
        return obj.vessel.name if obj.vessel else ''
    
    def get_maker(self, obj):
        return obj.maker.name if obj.maker else ''
    
    def get_makerType(self, obj):
        return obj.makerType.type if obj.makerType else ''
    
    class Meta:
        exclude = ('customer',)
    
class RequestPartListSerializer2(serializers.ModelSerializer):
    theRequest = RequestListSerializer()
    user = UserListSerializer()
    part = PartListSerializer()
    class Meta:
        model = RequestPart
        fields = ["id", "user", "sessionKey", "id", "theRequest", "part", "quantity", "sequency"]
        
class RequestPartListSerializer(serializers.Serializer):
    theRequestId = serializers.SerializerMethodField()
    partNo = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    sessionKey = serializers.CharField()
    quantity = serializers.FloatField()
    sequency = serializers.IntegerField()
    warehouse = serializers.SerializerMethodField()
    stockCode = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    
    def get_theRequestId(self, obj):
        return obj.theRequest.pk if obj.theRequest else ''
    
    def get_partNo(self, obj):
        return obj.part.partNo if obj.part else ''
    
    def get_description(self, obj):
        return obj.part.description if obj.part else ''
    
    def get_unit(self, obj):
        return obj.part.unit if obj.part else ''
    
    def get_warehouse(self, obj):
        if obj.part.item_part.first():
            return obj.part.item_part.select_related("warehouse").filter().order_by("itemDate").first().warehouse.name if obj.part.item_part.first().warehouse else ''
        else:
            return ""
    def get_stockCode(self, obj):
        return obj.part.item_part.select_related().filter().order_by("itemDate").first().itemNo if obj.part.item_part.first() else ''
    
    def get_stock(self, obj):
        return obj.part.item_part.select_related().filter().order_by("itemDate").first().quantity if obj.part.item_part.first() else '0'
    
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
    
    
        
class InquiryListSerializer2(serializers.ModelSerializer):
    project = ProjectListSerializer()
    theRequest = RequestListSerializer()
    supplier = CompanyListSerializer()
    currency = CurrencyListSerializer()
    
    class Meta:
        model = Inquiry
        fields = ["id", "project", "theRequest", "identificationCode", "yearCode", "code", "inquiryNo", "supplier", "supplierRef",  "inquiryDate", "currency", "sessionKey", "totalTotalPrice"]

class InquiryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    projectCreator = serializers.SerializerMethodField()
    projectStage = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    makerType = serializers.SerializerMethodField()
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
    
    def get_customer(self, obj):
        return obj.theRequest.customer.name if obj.theRequest.customer else ''
    
    def get_vessel(self, obj):
        return obj.theRequest.vessel.name if obj.theRequest.vessel else ''
    
    def get_maker(self, obj):
        return obj.theRequest.maker.name if obj.theRequest.maker else ''
    
    def get_makerType(self, obj):
        return obj.theRequest.makerType.type if obj.theRequest.makerType else ''
    
    def get_supplier(self, obj):
        return obj.supplier.name if obj.supplier else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
     
    
class InquiryPartListSerializer2(serializers.ModelSerializer):
    inquiry = InquiryListSerializer()
    user = UserListSerializer()
    maker = MakerListSerializer()
    makerType = MakerTypeListSerializer()
    requestPart = RequestPartListSerializer()
    class Meta:
        model = InquiryPart
        fields = ["user", "sessionKey", "id", "inquiry", "maker", "makerType", "requestPart", "quantity", "sequency", "unitPrice", "totalPrice", "availability", "availabilityType"]

class InquiryPartListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    partNo = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    sessionKey = serializers.CharField()
    quantity = serializers.FloatField()
    sequency = serializers.IntegerField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    availability = serializers.IntegerField()
    availabilityType = serializers.CharField()
    partDetails = serializers.SerializerMethodField()
    note = serializers.CharField(allow_blank=True)
    remark = serializers.CharField(allow_blank=True)
    
    def get_partNo(self, obj):
        return obj.requestPart.part.partNo if obj.requestPart.part else ''
    
    def get_description(self, obj):
        return obj.requestPart.part.description if obj.requestPart.part else ''
    
    def get_unit(self, obj):
        return obj.requestPart.part.unit if obj.requestPart.part else ''
    
    def get_currency(self, obj):
        return obj.inquiry.currency.symbol if obj.inquiry.currency else ''
    
    def get_partDetails(self, obj):
        inquiryPartsList = []
        inquiryParts = InquiryPart.objects.select_related("inquiry","inquiry__currency").filter(requestPart__part = obj.requestPart.part).exclude(id = obj.id).order_by("-id")
        
        for index, inquiryPart in enumerate(inquiryParts):
            inquiryPartsList.append({"date":inquiryPart.inquiry.inquiryDate.strftime("%d.%m.%Y"),"inquiry":inquiryPart.inquiry.inquiryNo,"unitPrice":round(inquiryPart.unitPrice,2),"currency":inquiryPart.inquiry.currency.symbol})
            if index == 2:
                break
            
        return {
            "group": obj.requestPart.part.group if obj.requestPart.part else '',
            "manufacturer": obj.requestPart.part.manufacturer if obj.requestPart.part else '',
            "crossRef": obj.requestPart.part.crossRef if obj.requestPart.part else '',
            "ourRef": obj.requestPart.part.ourRef if obj.requestPart.part else '',
            "quantity": obj.requestPart.part.quantity if obj.requestPart.part else '',
            "buyingPrice": obj.requestPart.part.buyingPrice if obj.requestPart.part else '',
            "retailPrice": obj.requestPart.part.retailPrice if obj.requestPart.part else '',
            "dealerPrice": obj.requestPart.part.group if obj.requestPart.part else '',
            "lastParts" : inquiryPartsList
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
    
    
    
class QuotationListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    projectCreator = serializers.SerializerMethodField()
    projectStage = serializers.SerializerMethodField()
    customerId = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    customerRef = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    makerType = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    soc = serializers.CharField()
    quotationNo = serializers.CharField()
    quotationDate = serializers.DateField()
    approval = serializers.CharField()
    approvalClass = serializers.CharField()
    sessionKey = serializers.CharField()
    totalDiscountPrice = serializers.FloatField()
    totalBuyingPrice = serializers.FloatField()
    totalSellingPrice = serializers.FloatField()
    parts = serializers.SerializerMethodField()
    
    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def get_projectNo(self, obj):
        return obj.project.projectNo if obj.project else ''
    
    def get_projectCreator(self, obj):
        return obj.project.user.first_name + " " + obj.project.user.last_name if obj.project.user else ''
    
    def get_projectStage(self, obj):
        return obj.project.stage if obj.project else ''
    
    def get_customerId(self, obj):
        return obj.inquiry.theRequest.customer.id if obj.inquiry.theRequest.customer else ''
    
    def get_customer(self, obj):
        return obj.inquiry.theRequest.customer.name if obj.inquiry.theRequest.customer else ''
    
    def get_vessel(self, obj):
        return obj.inquiry.theRequest.vessel.name if obj.inquiry.theRequest.vessel else ''
    
    def get_customerRef(self, obj):
        return obj.inquiry.theRequest.customerRef if obj.inquiry.theRequest else ''
    
    def get_maker(self, obj):
        return obj.inquiry.theRequest.maker.name if obj.inquiry.theRequest.maker else ''
    
    def get_makerType(self, obj):
        return obj.inquiry.theRequest.makerType.type if obj.inquiry.theRequest.makerType else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
    
    def get_parts(self, obj):
        return len(QuotationPart.objects.filter(quotation=obj))
        
    # def get_inquiry(self, obj):
    #     inquiry_obj = obj.inquiry
    #     if inquiry_obj is not None:
    #         customer_name = inquiry_obj.theRequest.customer.name if inquiry_obj.theRequest.customer else None
    #         vessel_name = inquiry_obj.theRequest.vessel.name if inquiry_obj.theRequest.vessel else None
             
    #         return {
    #             "id": inquiry_obj.id,
    #             "customer": customer_name,
    #             "vessel": vessel_name,
    #             "customerRef": inquiry_obj.theRequest.customerRef
    #         }
    #     return None
    
    
    
    # class Meta:
    #     model = Quotation
    #     fields = ["id", "project", "inquiry", "soc", "identificationCode", "yearCode", "code", "quotationNo", "quotationDate", "person", "approval","approvalClass", "currency","sessionKey","totalDiscountPrice", "totalBuyingPrice","totalSellingPrice"]

class QuotationCustomerListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
       
class QuotationPartListSerializer2(serializers.ModelSerializer):
    quotation = QuotationListSerializer()
    user = UserListSerializer()
    maker = MakerListSerializer()
    makerType = MakerTypeListSerializer()
    inquiryPart = InquiryPartListSerializer()
    class Meta:
        model = QuotationPart
        fields = ["user", "sessionKey", "id", "quotation", "maker", "makerType", "inquiryPart", "quantity", "sequency", "unitPrice1", "totalPrice1", "unitPrice2", "totalPrice2", "unitPrice3", "totalPrice3", "profit", "discount", "availability","availabilityChar", "availabilityType", "note", "remark"]

    
    
class QuotationPartListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quotationId = serializers.SerializerMethodField()
    partNo = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    requestPart = serializers.SerializerMethodField()
    sessionKey = serializers.CharField()
    quantity = serializers.FloatField()
    sequency = serializers.IntegerField()
    unitPrice1 = serializers.FloatField()
    unitPrice2 = serializers.FloatField()
    unitPrice3 = serializers.FloatField()
    totalPrice1 = serializers.FloatField()
    totalPrice2 = serializers.FloatField()
    totalPrice3 = serializers.FloatField()
    profit = serializers.FloatField()
    discount = serializers.FloatField()
    availability = serializers.IntegerField()
    availabilityChar = serializers.CharField()
    availabilityType = serializers.CharField()
    note = serializers.CharField(allow_blank=True)
    remark = serializers.CharField(allow_blank=True)
    alternative = serializers.BooleanField()
    currency = serializers.SerializerMethodField()
    partDetails = serializers.SerializerMethodField()
    
    def get_quotationId(self, obj):
        return obj.quotation.id if obj.quotation else ''

    def get_partNo(self, obj):
        return obj.inquiryPart.requestPart.part.partNo if obj.inquiryPart.requestPart.part else ''
    
    def get_description(self, obj):
        return obj.inquiryPart.requestPart.part.description if obj.inquiryPart.requestPart.part else ''
    
    def get_unit(self, obj):
        return obj.inquiryPart.requestPart.part.unit if obj.inquiryPart.requestPart.part else ''
    
    def get_supplier(self, obj):
        return obj.inquiryPart.inquiry.supplier.name if obj.inquiryPart else ''
    
    def get_requestPart(self, obj):
        return obj.inquiryPart.requestPart.id if obj.inquiryPart.requestPart else ''

    def get_currency(self, obj):
        return obj.quotation.currency.symbol if obj.quotation.currency else ''
    
    def get_partDetails(self, obj):
        quotationPartsList = []
        quotationParts = QuotationPart.objects.select_related("quotation","quotation__currency").filter(inquiryPart__requestPart__part = obj.inquiryPart.requestPart.part).exclude(id = obj.id).order_by("-id")
        for index, quotationPart in enumerate(quotationParts):
            quotationPartsList.append({"date":quotationPart.quotation.quotationDate.strftime("%d.%m.%Y"),"project":quotationPart.quotation.project.projectNo,"unitPrice3":round(quotationPart.unitPrice3,2),"currency":quotationPart.quotation.currency.symbol})
            if index == 2:
                break
        return {
            "group": obj.inquiryPart.requestPart.part.group if obj.inquiryPart.requestPart.part else '',
            "manufacturer": obj.inquiryPart.requestPart.part.manufacturer if obj.inquiryPart.requestPart.part else '',
            "crossRef": obj.inquiryPart.requestPart.part.crossRef if obj.inquiryPart.requestPart.part else '',
            "ourRef": obj.inquiryPart.requestPart.part.ourRef if obj.inquiryPart.requestPart.part else '',
            "quantity": obj.inquiryPart.requestPart.part.quantity if obj.inquiryPart.requestPart.part else '',
            "buyingPrice": obj.inquiryPart.requestPart.part.buyingPrice if obj.inquiryPart.requestPart.part else '',
            "retailPrice": obj.inquiryPart.requestPart.part.retailPrice if obj.inquiryPart.requestPart.part else '',
            "dealerPrice": obj.inquiryPart.requestPart.part.group if obj.inquiryPart.requestPart.part else '',
            "lastParts" : quotationPartsList
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

class QuotationExtraListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quotationId = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField()
    sessionKey = serializers.CharField()
    quantity = serializers.FloatField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    
    def get_quotationId(self, obj):
        return obj.quotation.id if obj.quotation else ''
    
    def get_unit(self, obj):
        return obj.inquiryPart.requestPart.part.unit if obj.inquiryPart.requestPart.part else ''

    def get_currency(self, obj):
        return obj.quotation.currency.symbol if obj.quotation.currency else ''

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
  
class OrderConfirmationListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    projectCreator = serializers.SerializerMethodField()
    projectStage = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    customerRef = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    makerType = serializers.SerializerMethodField()
    quotationId = serializers.SerializerMethodField()
    orderConfirmationNo = serializers.CharField()
    orderConfirmationDate = serializers.DateField()
    totalSellingPrice = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    
    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def get_projectNo(self, obj):
        return obj.project.projectNo if obj.project else ''
    
    def get_projectCreator(self, obj):
        return obj.project.user.first_name + " " + obj.project.user.last_name if obj.project.user else ''
    
    def get_projectStage(self, obj):
        return obj.project.stage if obj.project else ''
    
    def get_customer(self, obj):
        return obj.quotation.inquiry.theRequest.customer.name if obj.quotation.inquiry.theRequest.customer else ''
    
    def get_vessel(self, obj):
        return obj.quotation.inquiry.theRequest.vessel.name if obj.quotation.inquiry.theRequest.vessel else ''
    
    def get_customerRef(self, obj):
        return obj.quotation.inquiry.theRequest.customerRef if obj.quotation.inquiry.theRequest else ''
    
    def get_maker(self, obj):
        return obj.quotation.inquiry.theRequest.maker.name if obj.quotation.inquiry.theRequest.maker else ''
    
    def get_makerType(self, obj):
        return obj.quotation.inquiry.theRequest.makerType.type if obj.quotation.inquiry.theRequest.makerType else ''
    
    def get_quotationId(self, obj):
        return obj.quotation.id if obj.quotation else ''
    
    def get_currency(self, obj):
        return obj.quotation.currency.code if obj.quotation.currency else ''
    
    def get_totalSellingPrice(self, obj):
        vatAmount = obj.quotation.totalSellingPrice * (obj.vat/100)
        return obj.quotation.totalSellingPrice + vatAmount if obj.quotation else ''

class OrderConfirmationCustomerListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class OrderNotConfirmationListSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer()
    quotation = QuotationListSerializer()
    
    class Meta:
        model = OrderNotConfirmation
        fields = ["id", "project", "quotation", "identificationCode", "yearCode", "code", "orderNotConfirmationNo", "orderNotConfirmationDate", ]
        
class PurchaseOrderListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    projectCreator = serializers.SerializerMethodField()
    projectStage = serializers.SerializerMethodField()
    supplierId = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    supplierRef = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    makerType = serializers.SerializerMethodField()
    purchaseOrderNo = serializers.CharField()
    purchaseOrderDate = serializers.DateField()
    totalTotalPrice = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    
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
    
    def get_customer(self, obj):
        return obj.inquiry.theRequest.customer.name if obj.inquiry.theRequest.customer else ''
    
    def get_vessel(self, obj):
        return obj.inquiry.theRequest.vessel.name if obj.inquiry.theRequest.vessel else ''
    
    def get_supplierRef(self, obj):
        return obj.inquiry.supplierRef if obj.inquiry else ''
    
    def get_maker(self, obj):
        return obj.inquiry.theRequest.maker.name if obj.inquiry.theRequest.maker else ''
    
    def get_makerType(self, obj):
        return obj.inquiry.theRequest.makerType.type if obj.inquiry.theRequest.makerType else ''
    
class PurchaseOrderSupplierListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    
class PurchaseOrderCustomerListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    
class PurchaseOrderVesselListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
 

class PurchaseOrderPartListSerializer2(serializers.ModelSerializer):
    purchaseOrder = PurchaseOrderListSerializer()
    user = UserListSerializer()
    maker = MakerListSerializer()
    makerType = MakerTypeListSerializer()
    inquiryPart = InquiryPartListSerializer()
    class Meta:
        model = PurchaseOrderPart
        fields = ["user", "sessionKey", "id", "purchaseOrder", "maker", "makerType", "inquiryPart", "quantity", "sequency", "unitPrice", "totalPrice", "availability", "availabilityType", "quality", "orderType"]


class PurchaseOrderPartListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    purchaseOrderId = serializers.SerializerMethodField()
    partNo = serializers.SerializerMethodField()
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
    
    def get_purchaseOrderId(self, obj):
        return obj.purchaseOrder.id if obj.purchaseOrder else ''
    
    def get_partNo(self, obj):
        return obj.inquiryPart.requestPart.part.partNo if obj.inquiryPart.requestPart.part else ''
    
    def get_description(self, obj):
        return obj.inquiryPart.requestPart.part.description if obj.inquiryPart.requestPart.part else ''
    
    def get_unit(self, obj):
        return obj.inquiryPart.requestPart.part.unit if obj.inquiryPart.requestPart.part else ''
    
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

class CollectionListSerializer(serializers.ModelSerializer):
    agent = CompanyListSerializer()
    
    class Meta:
        model = Collection
        fields = ["id", "trackingNo", "port", "transportationCompany", "waybillNo", "agent"]
        
class OrderTrackingListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    projectCreator = serializers.SerializerMethodField()
    projectStage = serializers.SerializerMethodField()
    projectDate = serializers.SerializerMethodField()
    customerId = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    customerRef = serializers.SerializerMethodField()
    purchaseOrders = serializers.SerializerMethodField()
    collections = CollectionListSerializer(many=True, source='collection_set')
    items = serializers.JSONField()
    collected = serializers.BooleanField()
    delivered = serializers.BooleanField()
    sendInvoiced = serializers.BooleanField()
    created_date = serializers.DateTimeField(format="%d.%m.%Y", required=False, read_only=True)
    
    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def get_projectNo(self, obj):
        return obj.project.projectNo if obj.project else ''
    
    def get_projectCreator(self, obj):
        return obj.project.user.first_name + " " + obj.project.user.last_name if obj.project.user else ''
    
    def get_projectStage(self, obj):
        
        return obj.project.stage if obj.project else ''
    def get_projectDate(self, obj):
        return obj.theRequest.requestDate if obj.theRequest else ''
    
    def get_customerId(self, obj):
        return obj.theRequest.customer.id if obj.theRequest.customer else ''
    
    def get_customer(self, obj):
        return obj.theRequest.customer.name if obj.theRequest.customer else ''
    
    def get_vessel(self, obj):
        return obj.theRequest.vessel.name if obj.theRequest.vessel else ''
    
    def get_customerRef(self, obj):
        return obj.theRequest.customerRef if obj.theRequest else ''
    
    def get_purchaseOrderStatuses(self, obj):
        return [purchaseOrder.status for purchaseOrder in obj.purchaseOrders.all()]
    
    def get_purchaseOrders(self, obj):
        purchaseOrders = obj.purchaseOrders.all()  # ManyToManyField'dan tüm ilişkili nesneleri al
        items_list = []
        for item in purchaseOrders:
            customer_name = item.inquiry.theRequest.customer.name if item.inquiry.theRequest.customer else None
            vessel_name = item.inquiry.theRequest.vessel.name if item.inquiry.theRequest.vessel else None
            maker_name = item.inquiry.theRequest.maker.name if item.inquiry.theRequest.maker else None
            makerType_type = item.inquiry.theRequest.makerType.type if item.inquiry.theRequest.makerType else None
            
            items_list.append({
                "id": item.id,
                "purchaseOrder": item.purchaseOrderNo,
                "supplier": item.inquiry.supplier.name,
                "customer": customer_name,
                "vessel": vessel_name,
                "maker": maker_name,
                "makerType": makerType_type,
                "status": item.orderConfirmation.status,
                "sendInvoiced": item.orderConfirmation.sendInvoiced,
                "proformaInvoiced": item.orderConfirmation.proformaInvoiced,
                "ocId" : item.orderConfirmation.id,
                "orderConfirmationNo" : item.orderConfirmation.orderConfirmationNo,
                "orderConfirmationDate" : item.orderConfirmation.orderConfirmationDate,
                "currency": item.currency.symbol
            })
        return items_list

class DispatchOrderListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sourceCompany = serializers.SerializerMethodField()
    dispatchOrderNo = serializers.CharField()

    def get_sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ''

class DispatchOrderPartListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    dispatchOrderId = serializers.SerializerMethodField()
    partNo = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    quantity = serializers.FloatField()
    sequency = serializers.IntegerField()
    note = serializers.CharField(allow_blank=True)
    remark = serializers.CharField(allow_blank=True)
    
    def get_dispatchOrderId(self, obj):
        return obj.dispatchOrder.id if obj.dispatchOrder else ''
    
    def get_partNo(self, obj):
        return obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.partNo if obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part else ''
    
    def get_description(self, obj):
        return obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.description if obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part else ''
    
    def get_unit(self, obj):
        return obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.unit if obj.collectionPart.purchaseOrderPart.inquiryPart.requestPart.part else ''
    
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


class ReportListSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    totalUSD = serializers.SerializerMethodField()
    totalEUR = serializers.SerializerMethodField()
    totalTRY = serializers.SerializerMethodField()
    totalRUB = serializers.SerializerMethodField()
    
    def get_type(self, obj):
        return type(obj)._meta.model_name if obj else ''
    
    def get_totalUSD(self, obj):
        if type(obj)._meta.model_name == "orderconfirmation":
            return obj.project.projectNo if obj.project else ''
    
    
       
