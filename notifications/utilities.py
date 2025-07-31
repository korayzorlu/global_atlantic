from notifications.models import Notification

def create_notification(to_user, notification_type, url_key, relationed_object_id=0, optional_id = None): 
    if optional_id: 
        notification = Notification.objects.create(to_user=to_user, notification_type=notification_type, url_key=url_key, relationed_object_id=relationed_object_id, optional_id = optional_id)
    else:
        notification = Notification.objects.create(to_user=to_user, notification_type=notification_type, url_key=url_key, relationed_object_id=relationed_object_id)