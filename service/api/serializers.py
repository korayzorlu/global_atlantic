from rest_framework import serializers

from rest_framework.utils import html, model_meta, representation

from service.models import Offer, OfferServiceCard, OfferExpense, OfferPart,AcceptanceServiceCard,Acceptance,OfferNote
from account.models import SendInvoice
from django.contrib.auth.models import User

from card.api.serializers import CompanyListSerializer, VesselListSerializer, PersonListSerializer, CurrencyListSerializer, EnginePartListSerializer
from data.api.serializers import MakerListSerializer, MakerTypeListSerializer, PartListSerializer, ServiceCardListSerializer, ExpenseListSerializer
from user.api.serializers import UserListSerializer

class AcceptanceListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    customer = serializers.SerializerMethodField()
    acceptanceNo = serializers.CharField()
    acceptanceDate = serializers.DateField()
    created_date = serializers.DateTimeField(format="%d.%m.%Y", required=False, read_only=True)
    status = serializers.CharField(source='get_status_display')
    
    def get_customer(self, obj):
        return obj.customer.name if obj.customer else ''

class AcceptanceEquipmentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    acceptanceId = serializers.SerializerMethodField()
    serialNo = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    makerType = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sessionKey = serializers.CharField()
    quantity = serializers.FloatField()
    cyl = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    
    def get_acceptanceId(self, obj):
        return obj.acceptance.id if obj.acceptance else ''

    def get_serialNo(self, obj):
        return obj.equipment.serialNo if obj.equipment else ''
    
    def get_maker(self, obj):
        return obj.equipment.maker.name if obj.equipment else ''
    
    def get_makerType(self, obj):
        return obj.equipment.makerType.type if obj.equipment else ''
    
    def get_category(self, obj):
        return obj.equipment.category if obj.equipment else ''
    
    def get_cyl(self, obj):
        return obj.equipment.cyl if obj.equipment else ''
    
    def get_description(self, obj):
        return obj.equipment.description if obj.equipment else ''
    
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
 
class AcceptanceServiceCardListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    acceptanceId = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    sessionKey = serializers.CharField()
    quantity = serializers.FloatField()
    unitPrice1 = serializers.FloatField()
    unitPrice2 = serializers.FloatField()
    unitPrice3 = serializers.FloatField()
    totalPrice = serializers.FloatField()
    profit = serializers.FloatField()
    discount = serializers.FloatField()
    tax = serializers.FloatField()
    taxPrice = serializers.FloatField()
    note = serializers.CharField(allow_blank=True)
    remark = serializers.CharField(allow_blank=True)
    currency = serializers.SerializerMethodField()
    
    def get_acceptanceId(self, obj):
        return obj.acceptance.id if obj.acceptance else ''

    def get_code(self, obj):
        return obj.serviceCard.code if obj.serviceCard else ''
    
    def get_name(self, obj):
        return obj.serviceCard.name if obj.serviceCard else ''
    
    def get_about(self, obj):
        return obj.serviceCard.about if obj.serviceCard else ''
    
    def get_unit(self, obj):
        return obj.serviceCard.unit if obj.serviceCard else ''

    def get_currency(self, obj):
        return obj.acceptance.currency.symbol if obj.acceptance.currency else ''
    
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
 
class OfferListSerializerEx(serializers.ModelSerializer):
    user = UserListSerializer()
    customer = CompanyListSerializer()
    person = PersonListSerializer()
    vessel = VesselListSerializer()
    equipment = EnginePartListSerializer()
    currency = CurrencyListSerializer()
    created_date = serializers.DateTimeField(format="%d.%m.%Y", required=False, read_only=True)
    status = serializers.CharField(source='get_status_display')
    
    def to_internal_value(self, data):
        return Offer.objects.get(pk=data['id'])
    
    class Meta:
        model = Offer
        fields = ["user", "sessionKey", "id", "identificationCode", "yearCode", "code", "offerNo", "customer", "person", "vessel", "offerDate","note", "equipment","status","confirmed","finished", "currency","invoiced", "created_date"]
        
class OfferListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    customer = serializers.SerializerMethodField()
    person = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    equipmentMaker = serializers.SerializerMethodField()
    equipmentType = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    currencySymbol = serializers.SerializerMethodField()
    offerNo = serializers.CharField()
    offerDate = serializers.DateField()
    created_date = serializers.DateTimeField(format="%d.%m.%Y", required=False, read_only=True)
    status = serializers.CharField(source='get_status_display')
    invoiced = serializers.SerializerMethodField()
    sendInvoiced = serializers.BooleanField()
    
    def get_customer(self, obj):
        return obj.customer.name if obj.customer else ''
    
    def get_vessel(self, obj):
        return obj.vessel.name if obj.vessel else ''
    
    def get_person(self, obj):
        return obj.person.name if obj.person else ''
    
    def get_equipmentMaker(self, obj):
        return obj.equipment.maker.name if obj.equipment else ''
    
    def get_equipmentType(self, obj):
        return obj.equipment.makerType.type if obj.equipment else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
    
    def get_currencySymbol(self, obj):
        return obj.currency.symbol if obj.currency else ''
    
    def get_invoiced(self, obj):
        sendInvoice = SendInvoice.objects.select_related().filter(offer = obj).first()
        if sendInvoice:
            return True
        else:
            return False
        
class OfferServiceCardListSerializer2(serializers.ModelSerializer):
    offer = OfferListSerializer()
    user = UserListSerializer()
    class Meta:
        model = OfferServiceCard
        fields = ["id", "user", "sessionKey", "offer", "serviceCard", "quantity",
                  "unitPrice1", "unitPrice2", "unitPrice3", "totalPrice", "profit", "discount", "tax", "taxPrice", "extra", "note","remark"]

class OfferServiceCardListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    offerId = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    sessionKey = serializers.CharField()
    quantity = serializers.FloatField()
    unitPrice1 = serializers.FloatField()
    unitPrice2 = serializers.FloatField()
    unitPrice3 = serializers.FloatField()
    totalPrice = serializers.FloatField()
    profit = serializers.FloatField()
    discount = serializers.FloatField()
    tax = serializers.FloatField()
    taxPrice = serializers.FloatField()
    note = serializers.CharField(allow_blank=True)
    remark = serializers.CharField(allow_blank=True)
    currency = serializers.SerializerMethodField()
    
    def get_offerId(self, obj):
        return obj.offer.id if obj.offer else ''

    def get_code(self, obj):
        return obj.serviceCard.code if obj.serviceCard else ''
    
    def get_name(self, obj):
        return obj.serviceCard.name if obj.serviceCard else ''
    
    def get_about(self, obj):
        return obj.serviceCard.about if obj.serviceCard else ''
    
    def get_unit(self, obj):
        return obj.serviceCard.unit if obj.serviceCard else ''

    def get_currency(self, obj):
        return obj.offer.currency.symbol if obj.offer.currency else ''
    
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
   
class OfferExpenseListSerializer(serializers.ModelSerializer):
    offer = OfferListSerializer()
    user = UserListSerializer()
    expense = ExpenseListSerializer()
    class Meta:
        model = OfferExpense
        fields = ["id", "user", "sessionKey", "offer", "expense", "quantity",
                  "unitPrice", "totalPrice","extra"]
        
class OfferPartListSerializer2(serializers.ModelSerializer):
    offer = OfferListSerializer()
    user = UserListSerializer()
    part = PartListSerializer()
    class Meta:
        model = OfferPart
        fields = ["id", "user", "sessionKey", "offer", "part", "quantity",
                  "unitPrice", "totalPrice","extra", "remark"]
        
class OfferPartListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    partNo = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    sessionKey = serializers.CharField()
    quantity = serializers.FloatField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    remark = serializers.CharField(allow_blank=True)
    
    def get_partNo(self, obj):
        return obj.part.partNo if obj.part else ''
    
    def get_description(self, obj):
        return obj.part.description if obj.part else ''
    
    def get_unit(self, obj):
        return obj.part.unit if obj.part else ''
    
    def get_group(self, obj):
        return obj.part.group if obj.part else ''
    
    def get_currency(self, obj):
        return obj.offer.currency.symbol if obj.offer.currency else ''

    
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
        
class OfferNoteListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    userId = serializers.SerializerMethodField()
    offerId = serializers.SerializerMethodField()
    sessionKey = serializers.CharField()
    title = serializers.CharField()
    text = serializers.CharField()
    offerNoteDate = serializers.DateField()
    created_date = serializers.DateTimeField(format="%d.%m.%Y", required=False, read_only=True)
    
    def get_userId(self, obj):
        return obj.user.id if obj.user else ''
    
    def get_offerId(self, obj):
        return obj.offer.id if obj.offer else ''
    
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