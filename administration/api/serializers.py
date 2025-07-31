from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.utils import html, model_meta, representation

from administration.models import AccessAuthorization, DataAuthorization

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
    position = serializers.SerializerMethodField()
    
    def get_username(self, obj):
        return obj.user.username if obj.user else ''
    
    def get_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name if obj.user else ''
    
    def get_position(self, obj):
        return obj.positionType.name if obj.positionType else ''
    
class UserListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.SerializerMethodField()
    sourceCompany = serializers.SerializerMethodField()
    sourceCompanyId = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return obj.first_name + " " + obj.last_name if obj else ''
    
    def get_sourceCompany(self, obj):
        return obj.profile.sourceCompany.name if obj.profile.sourceCompany else ''
    
    def get_sourceCompanyId(self, obj):
        return obj.profile.sourceCompany.id if obj.profile.sourceCompany else ''
    
    def get_image(self, obj):
        return obj.profile.image.url if obj.profile.image else ''
    
    
    
class UserSourceCompanyListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    formalName = serializers.CharField()
    
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
    
class CompanyListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    formalName = serializers.CharField()
    companyNo = serializers.CharField()