from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.contrib.auth import login as authlogin,authenticate,update_session_auth_hash
from . models import Address
from shopping.models import Order,OrderItem

# Create your views here.
@never_cache
@login_required(login_url='/signIn')
def account(request):
    if request.user.is_superuser:
        return redirect('admin')
    user = request.user
    context = {
        'user':user
    }
    return render(request,'account.html',context)

@never_cache
@login_required(login_url='/signIn')
def address(request):
    if request.user.is_superuser:
        return redirect('admin')
    address = Address.objects.filter(userId=request.user)
    context = {
        'addresses':address
    }
    return render(request,'address.html',context)

@never_cache
@login_required(login_url='/signIn')
def order(request):
    if request.user.is_superuser:
        return redirect('admin')

    user_id = request.user.id
    orders = Order.objects.filter(userId=user_id).prefetch_related('orderId')

    context = {
        'orders': orders,
    }

    return render(request, 'order.html', context)


@never_cache
@login_required(login_url='/signIn')
def coupon(request):
    if request.user.is_superuser:
        return redirect('admin')
    return render(request,'coupon.html')

@never_cache
@login_required(login_url='/signIn')
def wellat(request):
    if request.user.is_superuser:
        return redirect('admin')
    return render(request,'wellat.html')

@never_cache
@login_required(login_url='/signIn')
def changePassword(request):
    if request.POST:
        currentPassword = request.POST.get('currentPassword')
        newPassword = request.POST.get('newPassword')
        confirmPassword = request.POST.get('confirmPassword')
        user = request.user

        if user.check_password(currentPassword):
            if newPassword == confirmPassword:
                user.set_password(confirmPassword)
                user.save()
                update_session_auth_hash(request,user)
                return redirect('account')
            else:
                print('not match')
        else:
            print('current not match')

    return render(request,'changePassword.html')

@never_cache
@login_required(login_url='/signIn')
def editProfile(request):
    user = User.objects.get(id=request.user.id)
    if request.POST:
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        username = request.POST.get('username')
        
        user.first_name = firstName
        user.last_name = lastName
        user.username = username

        user.save()
        return redirect('account')
    context = {
        'user':user
    }
    return render(request,'editProfile.html',context)

@never_cache
@login_required(login_url='/signIn')
def addAdress(request):
    if request.POST:
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        houseName = request.POST.get('houseName')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')
        zipCode = request.POST.get('zipCode')
        user = request.user

        address = Address.objects.create(name=name,phone=phone,houseName=houseName,city=city,district=district,state=state,zipCode=zipCode,userId=user)
        address.save()
        return redirect('address')
    return render(request,'addAddress.html')

@never_cache
@login_required(login_url='/signIn')
def editAddress(request,aId):
    addressId = Address.objects.get(id=aId)
    if request.POST:
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        houseName = request.POST.get('houseName')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')
        zipCode = request.POST.get('zipCode')

        addressId.name = name
        addressId.phone = phone
        addressId.houseName = houseName
        addressId.city = city
        addressId.district = district
        addressId.state = state
        addressId.zipCode = zipCode
        addressId.save()
        return redirect('address')
    context = {
        'address':addressId
    }
    return render(request,'editAddress.html',context)

@never_cache
@login_required(login_url='/signIn')
def removeAddress(request,aId):
    address = Address.objects.get(id=aId)
    address.delete()
    return redirect('address')