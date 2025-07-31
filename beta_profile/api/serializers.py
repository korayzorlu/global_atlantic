from django.contrib.auth.models import User
from rest_framework import serializers

from beta_profile.models import Document, Leave, Team, Department, Profile, EmployeeType, Record, Currency, Title


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = User
        fields = ["id", "full_name", "username", "first_name", "last_name", "email"]


class ProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class ProfileListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()

    class Meta:
        model = Profile
        fields = ["pk", "user"]


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
        fields = ["id", "name", "about", "members", "lead"]


class DepartmentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ["id", "name", "about"]


class EmployeeTypeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeType
        fields = ["id", "name", "about"]

class TitleListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Title
        fields = ["id", "name", "about"]



class RecordListSerializer(serializers.ModelSerializer):
    timesince = serializers.CharField(source='get_timesince')

    class Meta:
        model = Record
        fields = ['username', 'path', 'method', 'timesince']


class CurrencyListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = ["id", "name"]

class LeaveListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Leave
        fields = "__all__"

class LeaveCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Leave
        fields = "__all__"

    def validate(self, data):
        validated_data = super().validate(data)
        return validated_data

    def create(self, validated_data):
        instance = super().create(validated_data)
        return validated_data

class DocumentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = "__all__"

class DocumentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = "__all__"

    def validate(self, data):
        validated_data = super().validate(data)
        return validated_data

    def create(self, validated_data):
        instance = super().create(validated_data)
        return validated_data