from django.urls import path
from .views import trigger_notification

urlpatterns = [
    path('trigger-notification/<int:user_id>/', trigger_notification, name='trigger-notification'),
]