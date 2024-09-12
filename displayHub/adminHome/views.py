from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

# Create your views here.

@never_cache
@login_required(login_url='/admin/login')
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
    return render(request,'adminHome.html')

@never_cache
@login_required(login_url='/admin/login')
def allUsers(request):
    if not request.user.is_superuser:
        return redirect('home')
    allUsers = User.objects.all()
    return render(request,'users.html',{'allUsers':allUsers})