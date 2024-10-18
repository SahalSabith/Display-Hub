from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

# Create your views here.
# notifications/views.py
def send_notification(user, message):
    notification = Notification.objects.create(user=user, message=message)
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user.id}',
        {
            'type': 'send_notification',
            'notification': {
                'id': notification.id,
                'message': notification.message,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
            }
        }
    )
