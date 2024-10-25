from channels.generic.websocket import WebsocketConsumer
from .models import ChatGroup, GroupMessage
from django.shortcuts import get_object_or_404
import json
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from webpush import send_user_notification

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.chatroomName = self.scope['url_route']['kwargs']['chatroomName']
        self.chatroom = get_object_or_404(ChatGroup, groupName=self.chatroomName)

        async_to_sync(self.channel_layer.group_add)(
            self.chatroomName,
            self.channel_name
        )

        self.accept()

    def disconnect(self, closeCode):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroomName, 
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']
        user = self.user

        message = GroupMessage.objects.create(
            body=body,
            author=self.user,
            group=self.chatroom
        )

        if user.is_staff or user.is_superuser:
            chat_user = self.chatroom.user.get(is_superuser=False, is_staff=False)
            payload = {
                "head": "you've got message from DisplayHub!",
                "body": message.body,
                "icon": "https://st2.depositphotos.com/1874273/6627/v/450/depositphotos_66278313-stock-illustration-sign-letter-d.jpg",
                "url": "https://www.displayhub.store"
            }
            send_user_notification(user=chat_user, payload=payload, ttl=1000)
        else:
            admin = self.chatroom.user.get(is_superuser=True)
            payload = {
                "head": "DisplayHub!",
                "body": message.body,
                "icon": "https://st2.depositphotos.com/1874273/6627/v/450/depositphotos_66278313-stock-illustration-sign-letter-d.jpg",
                "url": "https://www.displayhub.store"
            }
            send_user_notification(user=admin, payload=payload, ttl=1000)
        
        event = {
            'type': 'messageHandler',
            'messageId': message.id
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroomName, 
            event
        )

    def messageHandler(self, event):
        messageId = event['messageId']
        message = GroupMessage.objects.get(id=messageId)

        context = {
            'message': message,
            'user': self.user,
        }
        html = render_to_string('partials/chatMessage_p.html', context=context)

        self.send(text_data=html)