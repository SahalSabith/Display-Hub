from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from .models import ChatGroup, GroupMessage
from .forms import ChatMessageCreateForm
from webpush import send_user_notification

@never_cache
@login_required(login_url='signIn')
def userMessage(request, chatroomName=None):
    # Retrieve the chat group or return 404 if not found
    chatGroups = get_object_or_404(ChatGroup, groupName=chatroomName)
    
    # Get the last 30 messages for the chat group
    chatMessages = chatGroups.chatMessage.all()[:30]
    
    form = ChatMessageCreateForm()

    # Check if the request is from HTMX (indicating a form submission)
    if request.htmx:
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            # Create a new message but don't save to DB yet
            message = form.save(commit=False)
            message.author = request.user
            message.group = chatGroups
            message.save()

            # Assuming admin user has id 1
            admin = User.objects.get(id=1)
            
            # Ensure the message body exists before sending it in the notification payload
            if form.cleaned_data.get('body'):
                payload = {
                    "head": f"You have a new message from {request.user.username}",
                    "body": form.cleaned_data['body'],
                    "icon": "https://st2.depositphotos.com/1874273/6627/v/450/depositphotos_66278313-stock-illustration-sign-letter-d.jpg",
                    "url": "https://www.displayhub.store"
                }
                # Send notification to the admin user
                send_user_notification(user=admin, payload=payload, ttl=1000)

            context = {
                'message': message,
                'user': request.user
            }
            # Render the new message without refreshing the entire page
            return render(request, 'partials/chatMessage_p.html', context)

    context = {
        'messages': chatMessages,
        'form': form,
        'chatroomName': chatroomName
    }

    return render(request, 'userChat.html', context)

def getOrCreateChatroom(request):
    # Get the admin user (consider using a more dynamic approach)
    admin = User.objects.get(pk=1)
    # Get all private chatrooms for the current user
    chatrooms = request.user.userChat.filter(isPrivate=True)

    if chatrooms.exists():
        # Check if user is already in an existing chatroom
        for chatroom in chatrooms:
            if request.user in chatroom.user.all():
                break
        else:
            # Create a new chatroom if user isn't in any existing ones
            chatroom = ChatGroup.objects.create(isPrivate=True)
            chatroom.user.add(request.user, admin)
    else:
        # Create a new chatroom if no private chatrooms exist
        chatroom = ChatGroup.objects.create(isPrivate=True)
        chatroom.user.add(request.user, admin)
    
    return redirect('messaging', chatroom.groupName)
