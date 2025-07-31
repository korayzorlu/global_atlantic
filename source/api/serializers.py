from rest_framework import serializers

from source.models import Company, Bank
from django.contrib.auth.models import User



class CompanyListSerializer(serializers.Serializer):
    country = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    name = serializers.CharField()
    formalName = serializers.CharField()
    companyNo = serializers.CharField()
    address = serializers.CharField()
    phone1 = serializers.CharField()
    vatOffice = serializers.CharField()
    vatNo = serializers.CharField()
    
    def get_country(self, obj):
        return obj.country.international_formal_name if obj.country else ''
    
    def get_city(self, obj):
        return obj.city.name if obj.city else ''

class BankListSerializer(serializers.Serializer):
    company = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    sessionKey = serializers.CharField()
    bankName = serializers.CharField()
    accountNo = serializers.CharField()
    ibanNo = serializers.CharField()
    accountType = serializers.CharField()
    swiftNo = serializers.CharField()
    branchName = serializers.CharField()
    branchCode = serializers.CharField()
    balance = serializers.CharField()
    
    def get_company(self, obj):
        return obj.company.name if obj.company else ''
    
    def get_user(self, obj):
        return obj.user.first_name + " " + obj.user.last_name if obj.user else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
