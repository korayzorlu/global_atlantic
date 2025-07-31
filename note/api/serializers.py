from rest_framework import serializers

from rest_framework.utils import html, model_meta, representation
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.contrib.auth.models import User



class NoteListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    userId = serializers.SerializerMethodField()
    sourceCompanyId = serializers.SerializerMethodField()
    title = serializers.CharField()
    text = serializers.CharField()
    created_date = serializers.DateTimeField(format="%d.%m.%Y", required=False, read_only=True)
    
    def get_userId(self, obj):
        return obj.user.id if obj.user else ''
    
    def get_sourceCompanyId(self, obj):
        return obj.sourceCompany.id if obj.sourceCompany else ''
    
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