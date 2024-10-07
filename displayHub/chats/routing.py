from django.urls import path
from .consumers import ChatroomConsumer

websocket_urlpatterns = [
    path('ws/chatroom/<chatroomName>',ChatroomConsumer.as_asgi()),
]