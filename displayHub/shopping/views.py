from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404
from adminManagements.models import Products,Brand,Category,Size,RefreshRate,Varients
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from . models import Cart,CartItem,Order,OrderItem
from django.db import IntegrityError
from django.urls import reverse
from userProfile.models import Address
import random
import string
from django.contrib import messages
from django.db.models import Count
from django.db import models
import json
from django.http import JsonResponse

# Create your views here.
@never_cache
@login_required(login_url='/signIn')
def cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(userId=user)
    cartItems = CartItem.objects.filter(cartId=cart)
    context = {
        'items': cartItems
    }
    
    return render(request, 'cart.html', context)

@never_cache
@login_required(login_url='/signIn')
def addToCart(request, pId):
    if request.POST:
        product = Varients.objects.get(id=pId)
        user = request.user
        quantity = request.POST.get('quantity', 1)
        if product.stock >= int(quantity):
            if CartItem.objects.filter(product=product).exists():
                return redirect('cart')
            else:
                cart, created = Cart.objects.get_or_create(userId=user)
                cartItem, created = CartItem.objects.get_or_create(product=product, quantity=quantity, cartId=cart)
                messages.success(request,"Product Suuccessfully Added")
                return redirect('cart')
        else:
            return redirect('productInfo',pId)
    else:
        return HttpResponseRedirect(reverse('productInfo', args=[pId]))

@never_cache
@login_required(login_url='/signIn')
def removeCart(request, cId):
    cartUser = get_object_or_404(Cart,userId=request.user)
    cartItem = CartItem.objects.get(cartId=cartUser,id=cId)
    cartItem.delete()
    return redirect('cart')

@never_cache
def products(request):
    productsList = Products.objects.all()
    sort = request.GET.get('sort')

    sizes = Size.objects.values('size').annotate(count=models.Count('size')).order_by('size')
    refreshRates = RefreshRate.objects.values('refreshRate').annotate(count=models.Count('refreshRate')).order_by('refreshRate')
    categories = Products.objects.values('category').annotate(count=models.Count('category')).order_by('category')

    if sort == 'price_asc':
        productsList = productsList.order_by('price')
    elif sort == 'price_desc':
        productsList = productsList.order_by('-price')
    elif sort == 'new_arrivals':
        productsList = productsList.order_by('-product__createdAt')
    elif sort == 'az':
        productsList = productsList.order_by('product__name')
    elif sort == 'za':
        productsList = productsList.order_by('-product__name')

    category = Category.objects.all()
    paginator = Paginator(productsList, 6)
    page_number = request.GET.get('page')

    try:
        products_final = paginator.get_page(page_number)
    except:
        products_final = paginator.page(paginator.num_pages)

    context = {
        'products': products_final,
        'categories': category,
        'sort': sort,
        'sizes': sizes,
        'category':categories,
        'refresh_rates': refreshRates,
    }
    return render(request, 'shop.html', context)

@never_cache
def productInfo(request, pId):
    product = Products.objects.get(id=pId)
    varientSize = product.varient.values('size_id', 'size__size').distinct()
    varientRefreshRates = product.varient.values('refreshRate_id', 'refreshRate__refreshRate').distinct()

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            size = data.get('size')
            refreshRate = data.get('refreshRate')

            # Initialize response data
            responseData = {}

            # Get refresh rates related to the selected size
            if size:
                refreshRatesForSize = Varients.objects.filter(
                    size_id=size,
                    product=product
                ).values('refreshRate_id', 'refreshRate__refreshRate').distinct()

                responseData['refreshRates'] = list(refreshRatesForSize)

            # Get sizes related to the selected refresh rate
            if refreshRate:
                sizesForRefreshRate = Varients.objects.filter(
                    refreshRate_id=refreshRate,
                    product=product
                ).values('size_id', 'size__size').distinct()

                responseData['size'] = list(sizesForRefreshRate)

            # Get the variant based on size and refresh rate (if both are selected)
            if size and refreshRate:
                selectedVarient = Varients.objects.filter(
                    size_id=size,
                    refreshRate_id=refreshRate,
                    product=product
                ).first()

                if selectedVarient:
                    responseData.update({
                        'price': selectedVarient.price,
                        'size': selectedVarient.size.size,
                        'refreshRate': selectedVarient.refreshRate.refreshRate,
                        'stock': selectedVarient.stock
                    })
                else:
                    responseData['error'] = 'No matching variant found.'

            return JsonResponse(responseData)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid request format'}, status=400)

    # For GET requests, return initial data
    context = {
        'product': product,
        'varientSize': varientSize,
        'varientRefreshRates': varientRefreshRates
    }
    return render(request, 'productInfo.html', context)


@never_cache
@login_required(login_url='/signIn')
def checkOut(request):
    user = request.user
    addresses = Address.objects.filter(userId=user)
    carts = Cart.objects.get(userId=user)
    cartItems = CartItem.objects.filter(cartId=carts)

    if not cartItems.exists():
        messages.error(request, 'Please add items to the cart')
        return redirect('cart')

    if request.POST:
        addressId = request.POST.get('address')
        address = Address.objects.get(id=addressId)
        paymentMethod = request.POST.get('paymentMethod')

        if not paymentMethod:
            messages.error(request, 'Please select a payment method.')
            request.session['show_error'] = True
            return redirect('checkOut')

        characters = string.ascii_letters + string.digits
        orderNumber = ''.join(random.choice(characters) for _ in range(10))
        print("Order Id is " + orderNumber)

        order = Order.objects.create(
            userId=user,
            addressId=address,
            paymentMethod=paymentMethod,
            orderNo=orderNumber,
            totalPrice=carts.cartTotal()
        )

        for item in cartItems:
            product = Varients.objects.get(id=item.product.pk)
            OrderItem.objects.create(
                orderId=order,
                product=product,
                quantity=item.quantity,
                totalPrice=item.productTotal()
            )

            product.stock -= item.quantity
            product.save()

        cartItems.delete()
        carts.delete()

        return redirect('order')

    if request.session.get('show_error'):
        del request.session['show_error']

    context = {
        'products': cartItems,
        'addresses': addresses,
        'cart':carts
    }
    return render(request, 'checkout.html', context)


@never_cache
@login_required(login_url='/signIn')
def orderDetails(request, oId):
    orderItem = OrderItem.objects.get(pk=oId)
    order = orderItem.orderId
    orders = OrderItem.objects.filter(orderId=order)

    context = {
        'order': order,
        'orders': orders,
        'orderItem':orderItem
    }
    return render(request, 'orderDetails.html', context)

@never_cache
@login_required(login_url='/signIn')
def cancelOrder(request, oId, oiId):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=oId)
            orderItem = OrderItem.objects.get(id=oiId)

            order.orderStatus = 'canceled'
            order.save()

            variant = orderItem.product
            variant.stock += orderItem.quantity
            variant.save()

            return HttpResponseRedirect(reverse('order'))

        except Order.DoesNotExist:
            pass
        except OrderItem.DoesNotExist:
            pass

    return redirect('order')