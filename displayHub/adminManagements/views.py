from django.shortcuts import render,redirect,get_object_or_404
from .models import Category,Brand,Products,Size,RefreshRate,Varients
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db import IntegrityError
from django.contrib import messages
import base64
from django.core.files.base import ContentFile
from shopping.models import Order,OrderItem
from django.http import HttpResponse, JsonResponse
import json


# Create your views here.
@never_cache
@login_required(login_url='/admin/login')
def addCategory(request):
    if not request.user.is_superuser:
        return redirect('home')
    if request.POST:
        name = request.POST.get('name')
        try:
            Category.objects.create(name=name)
            print("catogory created")
            return redirect('allCategory')
        except IntegrityError:
            messages.error(request,"Category Already Exits")
    return render(request,'addCategory.html')


@never_cache
@login_required(login_url='/admin/login')
def addBrand(request):
    if not request.user.is_superuser:
        return redirect('home')
    if request.POST:
        brand = request.POST.get('brand')
        try:
            Brand.objects.create(name=brand)
            print('brand added')
            return redirect('allBrand')
        except IntegrityError:
            messages.error(request,"The Brand Already Exits")
    return render(request,'addBrand.html')

@never_cache
@login_required(login_url='/admin/login')
def addSize(request):
    if request.method == "POST":
        data = json.loads(request.body)
        size = data.get('newSize')
        if size:
            newSize = Size.objects.create(size=size)
            newSize.save()
            return JsonResponse({'message': 'Size added successfully.', 'newSizeId': newSize.id})
        else:
            return JsonResponse({'error': 'Invalid size value.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@never_cache
@login_required(login_url='/admin/login')
def addRefreshRate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        refreshRate = data.get('newRefreshRate')
        if refreshRate:
            newRefreshRate = RefreshRate.objects.create(refreshRate=refreshRate)
            newRefreshRate.save()
            return JsonResponse({'message': 'Refresh rate added successfully.', 'newRefreshRateId': newRefreshRate.id})
        else:
            return JsonResponse({'error': 'Invalid refresh rate value.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@never_cache
@login_required(login_url='/admin/login')
def addProduct(request):
    if not request.user.is_superuser:
        return redirect('home')
    if request.POST:
        product = request.POST.get('product')
        resolution = request.POST.get('resolution')
        categoryId = request.POST.get('category')
        brandId = request.POST.get('brand')

        croppedImage1 = croppedImage2 = croppedImage3 = croppedImage4 = None

        croppedImage1 = request.POST.get('croppedImage1')
        croppedImage2 = request.POST.get('croppedImage2')
        croppedImage3 = request.POST.get('croppedImage3')
        croppedImage4 = request.POST.get('croppedImage4')

        def decode_base64_image(data):
            format, imgstr = data.split(';base64,') 
            ext = format.split('/')[-1] 
            img_data = ContentFile(base64.b64decode(imgstr), name=f"temp.{ext}")
            return img_data
        
        image1 = decode_base64_image(croppedImage1) if croppedImage1 else None
        image2 = decode_base64_image(croppedImage2) if croppedImage2 else None
        image3 = decode_base64_image(croppedImage3) if croppedImage3 else None
        image4 = decode_base64_image(croppedImage4) if croppedImage4 else None
        
        try:
            brand = Brand.objects.get(id=brandId)
            category = Category.objects.get(id=categoryId)

            Products.objects.create(
                name=product,
                resolution=resolution,
                category=category,
                brand=brand,
                image1=image1,
                image2=image2,
                image3=image3,
                image4=image4
                )
            
            print('product added')
            return redirect('allProducts')
        except IntegrityError:
            messages.error(request,"Product Must Be Unique")
    
    brands = Brand.objects.filter(status=True)
    category = Category.objects.filter(status=True)

    context = {
        'brands': brands,
        'categories':category,
    }
    return render(request,'addProduct.html',context)


@never_cache
@login_required(login_url='/admin/login')
def addVarient(request, vId):
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.POST:
        print(vId)
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        sizeId = request.POST.get('size')
        refreshRateId = request.POST.get('refreshRate')
        
        productId = Products.objects.get(id=vId)
        size = Size.objects.get(id=sizeId)
        refreshRate = RefreshRate.objects.get(id=refreshRateId)

        newVarient = Varients.objects.create(
            product=productId,
            stock=stock,
            price=price,
            refreshRate=refreshRate,
            size=size
        )
        
        print('Variant added')
        return redirect('allVarients', vId)
    
    sizes = Size.objects.all()
    refreshRates = RefreshRate.objects.all()

    context ={
        'sizes':sizes,
        'refreshRates':refreshRates
    }
    
    return render(request, 'addVarient.html',context)


@never_cache
@login_required(login_url='/admin/login')
def allVerients(request,vId):
    if not request.user.is_superuser:
        return redirect('home')
    varients = Varients.objects.filter(product=vId).order_by('-id')
    context = {
        'varients':varients,
        'vId':vId
    }
    return render(request,'allVarients.html',context)


@never_cache
@login_required(login_url='/admin/login')
def allProducts(request):
    if not request.user.is_superuser:
        return redirect('home')
    products = Products.objects.all().order_by('-id')
    context = {
        'products':products
    }
    return render(request,'allProducts.html',context)


@never_cache
@login_required(login_url='/admin/login')
def allCategory(request):
    if not request.user.is_superuser:
        return redirect('home')
    categories = Category.objects.all().order_by('-id')
    return render(request,'allCategory.html',{'categories':categories})


@never_cache
@login_required(login_url='/admin/login')
def allBrand(request):
    if not request.user.is_superuser:
        return redirect('home')
    brands = Brand.objects.all().order_by('-id')
    return render(request,'allBrand.html',{'brands':brands})


@never_cache
@login_required(login_url='/admin/login')
def blockBrand(request,bId):
    if not request.user.is_superuser:
        return redirect('home')
    brands = get_object_or_404(Brand,id=bId)
    brands.status = not brands.status
    brands.save()
    print('brand Blocked')
    return redirect('allBrand')


@never_cache
@login_required(login_url='/admin/login')
def blockProduct(request,pId):
    if not request.user.is_superuser:
        return redirect('home')
    product = get_object_or_404(Products,id=pId)
    product.status = not product.status
    product.save()
    print('varient added')
    return redirect('allProducts')

@never_cache
@login_required(login_url='/admin/login')
def blockCategory(request,cId):
    if not request.user.is_superuser:
        return redirect('home')
    category = get_object_or_404(Category,id=cId)
    category.status = not category.status
    category.save()
    return redirect('allCategory')


@never_cache
@login_required(login_url='/admin/login')
def editVarient(request, vId):
    if not request.user.is_superuser:
        return redirect('home')
    
    varient = Varients.objects.get(id=vId)
    pId = varient.product
    refreshRate = RefreshRate.objects.all()
    size = Size.objects.all()

    if request.POST:
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        sizeId = request.POST.get('size')
        refreshRateId = request.POST.get('refreshRate')

        varient.refreshRate = get_object_or_404(RefreshRate ,id=refreshRateId)
        varient.size = get_object_or_404(Size,id=sizeId)
        varient.price = price
        varient.stock = stock
        varient.save()

        messages.success(request, "Variant edited successfully")
        return redirect('allVarients', pId)

    context = {
        'variant': varient,
        'refreshRates': refreshRate,
        'size':size
    }

    return render(request, 'editVarients.html', context)



@never_cache
@login_required(login_url='/admin/login')
def editProduct(request,pId):
    if not request.user.is_superuser:
        return redirect('home')
    
    product = Products.objects.get(id=pId)
    brands = Brand.objects.all()
    categories = Category.objects.all()

    try:
        if request.POST:
            products = request.POST.get('product')
            brandId = request.POST.get('brand')
            categoryId = request.POST.get('category')
            resolution = request.POST.get('resolution')

            image1 = request.FILES.get('image1', None)
            image2 = request.FILES.get('image2', None)
            image3 = request.FILES.get('image3', None)
            image4 = request.FILES.get('image4', None)

            cropped_image1 = request.POST.get('croppedImage1', None)
            cropped_image2 = request.POST.get('croppedImage2', None)
            cropped_image3 = request.POST.get('croppedImage3', None)
            cropped_image4 = request.POST.get('croppedImage4', None)

            def decode_base64_image(data):
                if data and ';base64,' in data:
                    format, imgstr = data.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data = ContentFile(base64.b64decode(imgstr), name=f"temp.{ext}")
                    return img_data
                return None

            if cropped_image1:
                image1 = decode_base64_image(cropped_image1)
            if cropped_image2:
                image2 = decode_base64_image(cropped_image2)
            if cropped_image3:
                image3 = decode_base64_image(cropped_image3)
            if cropped_image4:
                image4 = decode_base64_image(cropped_image4)
            
            if image1:
                product.image1 = image1
            if image2:
                product.image2 = image2
            if image3:
                product.image3 = image3
            if image4:
                product.image4 = image4

            product.brand = get_object_or_404(Brand, id=brandId)
            product.category = get_object_or_404(Category, id=categoryId)
            product.name = products
            product.resolution = resolution
            product.save()

            messages.success(request,"Producted Edited succefully")
            return redirect('allProducts')
    except IntegrityError:
            messages.error(request,"Product Must Be Unique")
    
    context = {
        'product':product,
        'categories':categories,
        'brands':brands
    }

    return render(request,'editProduct.html',context)

@never_cache
@login_required(login_url='/admin/login')
def editCategory(request,cId):
    if not request.user.is_superuser:
        return redirect('home')
    category = Category.objects.get(id=cId)
    if request.POST:
        name = request.POST.get('name')
        try:
            category.name = name
            category.save()
            messages.success(request,"Category edited euccessfully")
            return redirect('allCategory')
        except IntegrityError:
            messages.error(request,"Category Already Exits")

    return render(request,'editCategory.html',{'category':category})

@never_cache
@login_required(login_url='/admin/login')
def editBrand(request,bId):
    if not request.user.is_superuser:
        return redirect('home')
    brand = Brand.objects.get(id=bId)
    if request.POST:
        brands = request.POST.get('brand')
        try:
            brand.name = brands
            brand.save()
            messages.success(request,"Brand edited sccessful")
            return redirect('allBrand')
        except IntegrityError:
            messages.error(request,"The Brand Already Exits")
    return render(request,'editBrand.html',{'brand':brand})


@never_cache
@login_required(login_url='/admin/login')
def listOrders(request):
    if not request.user.is_superuser:
        return redirect('home')
    orders = Order.objects.all().order_by('-id')
    context = {
        'orders': orders
    }
    return render(request, 'adminOrders.html', context)

@never_cache
@login_required(login_url='/admin/login')
def orderDetail(request, oId):
    if not request.user.is_superuser:
        return redirect('home')

    order = Order.objects.get(id=oId)
    orderItems = OrderItem.objects.filter(orderItemId=order)

    if not order:
        return redirect('admin') 

    if request.method == "POST":
        newStatus = request.POST.get("status")
        if newStatus in dict(Order.statusChoices).keys():
            order.orderStatus = newStatus
            order.save()

    context = {
        'order': order,
        'order_status_options': Order.statusChoices,
        'orderItem': orderItems,
    }
    return render(request, 'adminOrderDetails.html', context)

