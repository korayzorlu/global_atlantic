from django.core.validators import validate_email
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from hr.models import  TheCompany
from notifications.models import Notification
from utilities.send_mail import custom_send_mail

class NotificationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ["id", "is_read"]

    def validate(self, data):
        project = self.instance.get_relationed_object()
        try:
            validate_email(project.request.person_in_contact.email)
        except ValidationError as e:
            raise serializers.ValidationError(_('Person in contact of the customer has no email address.'))
        return data

    def update(self, instance, validated_data):
        instance = super().update(instance=instance, validated_data=validated_data)
        project = instance.get_relationed_object()
            
        custom_send_mail(
                _('Your order has been received!'),
                settings.DEFAULT_FROM_EMAIL,
                [project.request.person_in_contact.email],
                template_path='notification/mail/notified.html',
                context={'the_company': TheCompany.objects.get(id=1), 'project': project},
        )
        print("notification mailed")
        return instance
    

