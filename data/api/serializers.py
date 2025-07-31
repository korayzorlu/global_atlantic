from rest_framework import serializers
from django.shortcuts import render, redirect, get_object_or_404

from data.models import Maker, MakerType, PartUnique, Part, ServiceCard, Expense
from source.models import Company as SourceCompany
from user.api.serializers import UserListSerializer
from source.api.serializers import CompanyListSerializer as SourceCompanyListSerializer

from django.contrib.auth.models import User

class MakerListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    
    def to_internal_value(self, data):
        return Maker.objects.get(pk=data['id'])
    
    class Meta:
        model = Maker
        fields = ["id", "name", "info"]
        
class SourceCompanyForMakerTypeListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    
    def to_internal_value(self, data):
        return SourceCompany.objects.get(pk=data['id'])
    
    class Meta:
        model = Maker
        fields = ["id"]
        
class MakerTypeListSerializer(serializers.ModelSerializer):
    maker = MakerListSerializer()
    sourceCompany = SourceCompanyForMakerTypeListSerializer()
    
    class Meta:
        model = MakerType
        fields = ["id", "maker", "type", "name", "note","sourceCompany"]

# class MakerTypeListSerializer(serializers.Serializer):
#     maker = serializers.SerializerMethodField()
#     sourceCompany = serializers.SerializerMethodField()
#     id = serializers.IntegerField()
#     type = serializers.CharField()
#     name = serializers.CharField()
#     note = serializers.CharField()
    
#     def get_sourceCompany(self, obj):
#         return obj.sourceCompany.name if obj.sourceCompany else ''
    
#     def get_maker(self, obj):
#         return obj.maker.name if obj.maker else ''
    
#     def update(self, instance, validated_data):
#         info = model_meta.get_field_info(instance)
#         # Simply set each attribute on the instance, and then save it.
#         # Note that unlike `.create()` we don't need to treat many-to-many
#         # relationships as being a special case. During updates we already
#         # have an instance pk for the relationships to be associated with.
#         m2m_fields = []
#         for attr, value in validated_data.items():
#             if attr in info.relations and info.relations[attr].to_many:
#                 m2m_fields.append((attr, value))
#             else:
#                 setattr(instance, attr, value)

#         instance.save()

#         # Note that many-to-many fields are set after updating instance.
#         # Setting m2m fields triggers signals which could potentially change
#         # updated instance and we do not want it to collide with .update()
#         for attr, value in m2m_fields:
#             field = getattr(instance, attr)
#             field.set(value)

#         return instance
  
class PartUniqueListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartUnique
        fields = ["id", "code"]
        
class PartListSerializer2(serializers.ModelSerializer):
    partUnique = PartUniqueListSerializer()
    maker = MakerListSerializer()
    type = MakerTypeListSerializer()
    class Meta:
        model = Part
        fields = ["id", "partUnique", "partUniqueCode", "group", "unit", "description","techncialSpecification", "partNo", "maker", "manufacturer", "type","crossRef", "ourRef", "quantity", "drawingNr"]

class PartListSerializer(serializers.Serializer):
    sourceCompany = serializers.SerializerMethodField()
    partUnique = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    partUniqueCode = serializers.CharField()
    group = serializers.CharField()
    unit = serializers.CharField()
    description = serializers.CharField()
    techncialSpecification = serializers.CharField()
    partNo = serializers.CharField()
    manufacturer = serializers.CharField()
    crossRef = serializers.CharField()
    ourRef = serializers.CharField()
    quantity = serializers.FloatField()
    drawingNr = serializers.CharField()
    created_at = serializers.DateTimeField()
    warehouse = serializers.SerializerMethodField()
    stockCode = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    
    def get_sourceCompany(self, obj):
        return obj.sourceCompany.name if obj.sourceCompany else ''
    
    def get_partUnique(self, obj):
        return obj.partUnique.code if obj.partUnique else ''
    
    def get_maker(self, obj):
        return obj.maker.name if obj.maker else ''
    
    def get_type(self, obj):
        return obj.type.type if obj.type else ''
    
    def get_warehouse(self, obj):
        if obj.item_part.first():
            return obj.item_part.select_related("warehouse").filter().order_by("itemDate").first().warehouse.name if obj.item_part.select_related("warehouse").first().warehouse else ''
        else:
            return ""
    def get_stockCode(self, obj):
        return obj.item_part.select_related().filter().order_by("itemDate").first().itemNo if obj.item_part.first() else ''
    
    def get_stock(self, obj):
        return obj.item_part.select_related().filter().order_by("itemDate").first().quantity if obj.item_part.first() else '0'

class PartMakerListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    
class PartTypeListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    maker = serializers.SerializerMethodField()
    
    def get_maker(self, obj):
        return obj.maker.name if obj.maker else ''

class PartForTechnicalSpecificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ["id","techncialSpecification"]
       

class ServiceCardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCard
        fields = ["id", "code", "name", "group", "about", "unit"]
        
class ExpenseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "code", "name", "group", "description"]
        
# Add formlarına uyarlama
class UserAddListSerializer(serializers.ModelSerializer): #farklı app modellerinden foreign key varsa onun serializer'ını da aynı yere yazmak gerekiyor
    full_name = serializers.CharField(source='get_full_name')
    
    id = serializers.IntegerField(read_only=True)
    #başka bir yerden foreign key ile çağırılıyorsa datatables editor için gereken düzenleme
    def to_internal_value(self, data):
        return User.objects.get(pk=data['id'])

    class Meta:
        model = User
        fields = ["id", "full_name", "username", "first_name", "last_name", "email"]
        
class MakerTypeAddListSerializer(serializers.ModelSerializer):
    user = UserAddListSerializer()
    
    class Meta:
        model = MakerType
        fields = ["id", "user", "type", "name", "note", "sessionKey"]