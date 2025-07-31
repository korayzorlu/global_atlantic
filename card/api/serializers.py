from rest_framework import serializers
from rest_framework.utils import html, model_meta, representation

from card.models import Company, Country, City, Vessel, Person, Currency, Bank, EnginePart, Current, Owner, Billing

from django.contrib.auth.models import User

from data.api.serializers import MakerListSerializer, MakerTypeListSerializer
from administration.api.serializers import UserSourceCompanyListSerializer

class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "formal_name", "international_formal_name"]
        
class CityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "country"]
        
class CompanyListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sourceCompanyId = serializers.SerializerMethodField()
    role = serializers.JSONField()
    name = serializers.CharField()
    hesapKodu = serializers.CharField()
    country = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    phone1 = serializers.CharField()
    email = serializers.EmailField()
    companyNo = serializers.CharField()
    vatOffice = serializers.CharField()
    vatNo = serializers.CharField()

    def get_sourceCompanyId(self, obj):
        return obj.sourceCompany.id if obj.sourceCompany else ''
    
    def get_country(self, obj):
        return obj.country.international_formal_name if obj.country else ''
    
    def get_city(self, obj):
        return obj.city.name if obj.city else ''


class CurrencyListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    symbol = serializers.CharField()
    forexBuying = serializers.FloatField()
    forexSelling = serializers.FloatField()
    rateDate = serializers.DateField(format="%d.%m.%Y", required=False, read_only=True)
    sequency = serializers.IntegerField()

class CurrentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    company = serializers.SerializerMethodField()
    companyRole = serializers.SerializerMethodField()
    companyId = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    exchangeRate = serializers.SerializerMethodField()
    debt = serializers.FloatField()
    credit = serializers.FloatField()
    
    def get_company(self, obj):
        return obj.company.name if obj.company else ''
    
    def get_companyId(self, obj):
        return obj.company.id if obj.company else ''
    
    def get_companyRole(self, obj):
        return obj.company.role if obj.company else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
    
    def get_exchangeRate(self, obj):
        return obj.currency.forexSelling if obj.currency else ''


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]

class VesselListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sourceCompanyId = serializers.SerializerMethodField()
    name = serializers.CharField()
    company = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    building = serializers.CharField()
    type = serializers.CharField()
    imo = serializers.CharField()
    mmsi = serializers.CharField()

    def get_sourceCompanyId(self, obj):
        return obj.sourceCompany.id if obj.sourceCompany else ''
    
    def get_company(self, obj):
        return obj.company.name if obj.company else ''
    
    def get_owner(self, obj):
        return obj.owner.name if obj.owner else ''
    

        
class VesselHistoryListSerializer(serializers.Serializer):
    vessel = serializers.IntegerField()
    value = serializers.CharField()
    date = serializers.DateTimeField(format="%d.%m.%Y %H:%M:%S")
    status = serializers.CharField()
        
class EnginePartListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sourceCompanyId = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    makerType = serializers.SerializerMethodField()
    category = serializers.CharField()
    serialNo = serializers.CharField()
    cyl = serializers.CharField()
    version = serializers.CharField()
    description = serializers.CharField()

    def get_sourceCompanyId(self, obj):
        return obj.sourceCompany.id if obj.sourceCompany else ''
    
    def get_vessel(self, obj):
        return obj.vessel.name if obj.vessel else ''
    
    def get_maker(self, obj):
        return obj.maker.name if obj.maker else ''
    
    def get_makerType(self, obj):
        return obj.makerType.type if obj.makerType else ''
    
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
        
class PersonListSerializer(serializers.ModelSerializer):
    company = CompanyListSerializer()
    vessel = VesselListSerializer()
    user = UserListSerializer()
    class Meta:
        model = Person
        fields = ["user", "sessionKey", "id", "name", "company", "vessel", "title", "email", "phone"]
        
class BankListSerializer(serializers.ModelSerializer):
    company = CompanyListSerializer()
    user = UserListSerializer()
    currency = CurrencyListSerializer()
    class Meta:
        model = Bank
        fields = ["user", "sessionKey", "id", "company", "bankName", "accountNo", "ibanNo", "accountType", "swiftNo", "branchName", "branchCode", "currency"]
        
class OwnerListSerializer(serializers.ModelSerializer):
    vessel = VesselListSerializer()
    user = UserListSerializer()
    ownerCompany = CompanyListSerializer()
    class Meta:
        model = Owner
        fields = ["id", "user", "sessionKey", "id", "vessel", "ownerCompany"]
        
class BillingListSerializer2(serializers.ModelSerializer):
    vessel = VesselListSerializer()
    user = UserListSerializer()
    class Meta:
        model = Billing
        fields = ["id", "user", "sessionKey", "id", "vessel", "name", "address"]
        
class BillingInVesselListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    vesselId = serializers.SerializerMethodField()
    name = serializers.CharField()
    address = serializers.CharField()
    
    def get_vesselId(self, obj):
        return obj.vessel.id if obj.vessel else ''
    
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
    
class BillingListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    vessel = serializers.SerializerMethodField()
    name = serializers.CharField()
    address = serializers.CharField()
    hesapKodu = serializers.CharField()
    vatNo = serializers.CharField()
    
    def get_vessel(self, obj):
        return obj.vessel.name if obj.vessel else ''