from django.contrib.auth.models import User
from rest_framework import serializers

from user.models import Team, Department, Profile, EmployeeType, Record, Currency, Position, Education, AdditionalPayment



class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = User
        fields = ["id", "full_name", "username", "first_name", "last_name", "email"]


class ProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

class DepartmentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ["id", "name", "about"]

class PositionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = ["id","department", "name", "about", "parent", "position_level","sourceCompany"]

class ProfileListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    department = DepartmentListSerializer()
    positionType = PositionListSerializer()

    class Meta:
        model = Profile
        fields = ["pk", "user", "department", "positionType", "position", "image", "gender"]


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')
    profile = ProfileDetailSerializer()

    class Meta:
        model = User
        fields = ["id", "full_name", "username", "first_name", "last_name", "email", "profile"]


class ProfileThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["theme"]


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["image"]


class TeamListSerializer(serializers.ModelSerializer):
    members = UserListSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ["id", "name", "about", "members", "sourceCompany"]


class DepartmentListSerializer(serializers.ModelSerializer):
    members = ProfileListSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = ["id", "name", "about", "members", "sourceCompany"]


class EmployeeTypeListSerializer(serializers.ModelSerializer):
    members = ProfileListSerializer(many=True, read_only=True)

    class Meta:
        model = EmployeeType
        fields = ["id", "name", "about", "members","sourceCompany"]


class RecordListSerializer(serializers.ModelSerializer):
    timesince = serializers.CharField(source='get_timesince')

    class Meta:
        model = Record
        fields = ['username', 'path', 'method', 'timesince']


class CurrencyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ["id", "name"]

class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = User
        fields = ["id", "full_name", "username", "first_name", "last_name", "email"]
         
class EducationListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    educationProfile = ProfileListSerializer()
    class Meta:
        model = Education
        fields = ["id", "user", "sessionKey", "id", "educationProfile", "school", "department", "education_status", "startDate", "finishDate"]
        
class AdditionalPaymentListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    additionalPaymentProfile = ProfileListSerializer()
    class Meta:
        model = AdditionalPayment
        fields = ["id", "user", "sessionKey", "id", "additionalPaymentProfile", "amount", "payment_type", "additionalPaymentDate", "currency"] 
        
class AccessAuthorizationListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    
class DataAuthorizationListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    
class UserAuthorizationListSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    username = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    
    def get_username(self, obj):
        return obj.user.username if obj.user else ''
    
    def get_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name if obj.user else ''