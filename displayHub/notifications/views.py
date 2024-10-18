from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.http import JsonResponse
from asgiref.sync import sync_to_async 

# Create your views here.
# notifications/views.py
def send_notification(user, message):
    # Create the notification
    notification = Notification.objects.create(user=user, message=message)
    
    # Send the notification to the WebSocket group
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

# Use send_notification inside a view function
async def trigger_notification(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    message = "This is a test notification"
    await send_notification(user, message)
    return JsonResponse({'status': 'Notification sent successfully!'})