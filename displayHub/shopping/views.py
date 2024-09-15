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
from django.db.models import Min
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

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

@require_POST
@never_cache
@login_required(login_url='/signIn')
def updateQuantity(request):
    user = request.user
    data = json.loads(request.body)
    item_id = data.get('item_id')
    action = data.get('action')

    try:
        cart_item = CartItem.objects.get(id=item_id, cartId__userId=user)
        if action == 'increase':
            if cart_item.quantity < cart_item.varientId.stock:
                cart_item.quantity += 1
                cart_item.save()
                return JsonResponse({'success': True, 'new_quantity': cart_item.quantity})
            else:
                return JsonResponse({'success': False, 'error': 'Insufficient stock'})
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return JsonResponse({'success': True, 'new_quantity': cart_item.quantity})
            else:
                cart_item.delete()
                cart = cart_item.cartId
                cart.delete()
                return JsonResponse({'success': True, 'new_quantity': 0, 'removed': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@never_cache
@login_required(login_url='/signIn')
def addToCart(request, pId):
    if request.method == 'POST':
        # Fetch the session data
        session_data = request.session.get('product_data', None)

        if not session_data or 'variant_id' not in session_data:
            messages.error(request, "No variant selected or data missing.")
            return HttpResponseRedirect(reverse('productInfo', args=[pId]))

        variant_id = session_data.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))

        try:
            # Get the selected variant from the session
            variant = Varients.objects.get(id=variant_id)
        except Varients.DoesNotExist:
            messages.error(request, "Selected product variant does not exist.")
            return HttpResponseRedirect(reverse('productInfo', args=[pId]))

        # Check stock before adding to cart
        if variant.stock >= quantity:
            user = request.user
            # Get or create the user's cart
            cart, created = Cart.objects.get_or_create(userId=user)

            # Get or create the cart item
            cart_item, created = CartItem.objects.get_or_create(
                productId=variant.product,
                varientId=variant,
                cartId=cart,
                defaults={'quantity': quantity}
            )

            # If the cart item exists, update the quantity
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            # Clear the session product data
            request.session.pop('product_data', None)

            # Success message
            messages.success(request, "Product successfully added to cart.")
            return redirect('cart')
        else:
            messages.error(request, "Not enough stock available.")
            return HttpResponseRedirect(reverse('productInfo', args=[pId]))

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
    # Get the search query
    query = request.GET.get('q')

    # Get all products
    productsList = Products.objects.all()

    # Filter products based on search query
    if query:
        productsList = productsList.filter(name__icontains=query)  # Case-insensitive search on product name

    # Sorting logic
    sort = request.GET.get('sort')
    productsList = productsList.annotate(min_price=Min('varient__price'))

    if sort == 'price_asc':
        productsList = productsList.order_by('min_price')
    elif sort == 'price_desc':
        productsList = productsList.order_by('-min_price')
    elif sort == 'new_arrivals':
        productsList = productsList.order_by('-createdAt')
    elif sort == 'az':
        productsList = productsList.order_by('name')
    elif sort == 'za':
        productsList = productsList.order_by('-name')

    # Filter size, refresh rates, and categories (with counts)
    sizes = Size.objects.values('size').annotate(count=Count('size')).order_by('size')
    refreshRates = RefreshRate.objects.values('refreshRate').annotate(count=Count('refreshRate')).order_by('refreshRate')
    categories = Products.objects.values('category').annotate(count=Count('category')).order_by('category')

    # Pagination
    paginator = Paginator(productsList, 6)  # 6 products per page
    page_number = request.GET.get('page')

    try:
        products_final = paginator.get_page(page_number)
    except:
        products_final = paginator.page(paginator.num_pages)

    # Context for template
    context = {
        'products': products_final,
        'categories': Category.objects.all(),
        'sort': sort,
        'sizes': sizes,
        'category': categories,
        'refresh_rates': refreshRates,
        'query': query,  # Pass the search query to the template
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

            responseData = {}

            if size:
                refreshRatesForSize = Varients.objects.filter(
                    size_id=size,
                    product=product
                ).values('refreshRate_id', 'refreshRate__refreshRate').distinct()

                responseData['refreshRates'] = list(refreshRatesForSize)

            if refreshRate:
                sizesForRefreshRate = Varients.objects.filter(
                    refreshRate_id=refreshRate,
                    product=product
                ).values('size_id', 'size__size').distinct()

                responseData['size'] = list(sizesForRefreshRate)

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
                        'stock': selectedVarient.stock,
                        'variantId': selectedVarient.id
                    })
                    
                    request.session['product_data'] = {
                        'product_id': pId,
                        'variant_id': selectedVarient.id,
                        'price': selectedVarient.price,
                        'size': selectedVarient.size.size,
                        'refreshRate': selectedVarient.refreshRate.refreshRate,
                        'stock': selectedVarient.stock
                    }
                else:
                    responseData['error'] = 'No matching variant found.'

            return JsonResponse(responseData)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid request format'}, status=400)

    session_data = request.session.get('product_data', None)
    if session_data:
        context = {
            'product': product,
            'varientSize': varientSize,
            'varientRefreshRates': varientRefreshRates,
            'session_data': session_data
        }
    else:
        default_variant = product.varient.first()
        if default_variant:
            request.session['product_data'] = {
                'product_id': pId,
                'variant_id': default_variant.id,
                'price': default_variant.price,
                'size': default_variant.size.size,
                'refreshRate': default_variant.refreshRate.refreshRate,
                'stock': default_variant.stock
            }
            context = {
                'product': product,
                'varientSize': varientSize,
                'varientRefreshRates': varientRefreshRates,
                'session_data': request.session['product_data']
            }
        else:
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
            product = Products.objects.get(id=item.productId.id)
            varient = Varients.objects.get(id=item.varientId.id)
            orderItem = OrderItem.objects.create(
                orderItemId=order,
                productId=product,
                varientId=varient,
                quantity=item.quantity,
                totalPrice=item.cartItemTotal()
            )

            varient.stock -= item.quantity
            varient.save()

        cartItems.delete()
        carts.delete()

        return redirect('order')

    if request.session.get('show_error'):
        del request.session['show_error']

    context = {
        'products': cartItems,
        'addresses': addresses,
    }
    return render(request, 'checkout.html', context)


@never_cache
@login_required(login_url='/signIn')
def orderDetails(request, oId):
    order = Order.objects.get(id=oId)
    orderPk = order.pk

    orderItems = OrderItem.objects.filter(orderItemId=order)

    context = {
        'order': order,
        'orders': orderItems,
        'orderPk':orderPk
    }
    return render(request, 'orderDetails.html', context)

@require_POST
@never_cache
@login_required(login_url='/signIn')
def cancelOrder(request, oId):
    try:
        order = Order.objects.get(id=oId)
        if order.orderStatus not in ['canceled', 'delivered', 'refunded']:
            reason = request.POST.get('reason', '')
            if reason == 'other':
                other_reason = request.POST.get('other_reason', '')
                if other_reason:
                    reason = other_reason
                else:
                    return JsonResponse({'error': 'Please provide a reason for cancellation.'}, status=400)
            
            order.cancelReason = reason
            order.save()

            order.orderStatus = 'canceled'
            order.save()

            return JsonResponse({'success': True})

    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order does not exist'}, status=404)
    except OrderItem.DoesNotExist:
        return JsonResponse({'error': 'Order item does not exist'}, status=404)

    return JsonResponse({'error': 'Order cannot be canceled'}, status=400)

