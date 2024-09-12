from django.shortcuts import render,redirect
from adminManagements.models import Products
from django.views.decorators.cache import never_cache

# Create your views here.
@never_cache
def home(request):
    products = Products.objects.filter(status=True)
    return render(request,'index.html',{'products':products})

@never_cache
def contact(request):

    return render(request,'contact.html')