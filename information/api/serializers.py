from rest_framework import serializers

from information.models import Country, City, Company, Contact, Vessel, CompanyGroup
from user.api.serializers import UserListSerializer


class CityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        exclude = ["created_at", "updated_at"]


class CityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name"]


class CountryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        exclude = ["created_at", "updated_at"]


class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "formal_name"]


class CompanyGroupDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyGroup
        exclude = ["created_at", "updated_at"]


class CompanyGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyGroup
        fields = ["id", "name"]


class CompanyDetailSerializer(serializers.ModelSerializer):
    company_group = CompanyGroupListSerializer()
    country = CountryListSerializer()
    city = CityListSerializer()
    customer_representative = UserListSerializer()
    key_account = UserListSerializer()

    class Meta:
        model = Company
        exclude = ["created_at", "updated_at"]


class CompanyListSerializer(serializers.ModelSerializer):
    company_group = CompanyGroupListSerializer()
    country = CountryListSerializer()
    city = CityListSerializer()

    class Meta:
        model = Company
        fields = ["id", "name", "company_group", "country", "city", "company_type"]


class ContactDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = Contact
        exclude = ["created_at", "updated_at"]


class ContactListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = Contact
        fields = ["id", "full_name", "first_name", "last_name", "position", "phone_number", "email"]


class VesselDetailSerializer(serializers.ModelSerializer):
    manager_company = CompanyGroupListSerializer()
    owner_company = CompanyListSerializer()

    class Meta:
        model = Vessel
        exclude = ["created_at", "updated_at"]


class VesselListSerializer(serializers.ModelSerializer):
    manager_company = CompanyGroupListSerializer()
    owner_company = CompanyListSerializer()

    class Meta:
        model = Vessel
        fields = ["id", "status", "imo", "name", "manager_company", "owner_company", "flag"]
