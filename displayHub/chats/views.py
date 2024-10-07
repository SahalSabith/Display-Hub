from django.shortcuts import render,get_object_or_404,redirect
from .models import ChatGroup,GroupMessage
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import ChatMessageCreateForm

# Create your views here.
@never_cache
@login_required(login_url='signIn')
def userMessage(request):
    chatGroups = get_object_or_404(ChatGroup, groupName='newGroup')
    chatMessages = chatGroups.chatMessage.all()[:30]  # this for last 30 messages
    form =ChatMessageCreateForm()
    if request.htmx:
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chatGroups
            message.save()
            context = {
                'message':message,
                'user':request.user
            }
            return render(request,'partials/chatMessage_p.html',context)

    return render(request, 'userChat.html', {'messages': chatMessages,'form':form})