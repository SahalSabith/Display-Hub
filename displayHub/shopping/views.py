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
from discounts.models import Coupon

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
        # Retrieve session data
        session_data = request.session.get('product_data', None)
        if not session_data:
            messages.error(request, "No product data in session.")
            return HttpResponseRedirect(reverse('productInfo', args=[pId]))

        # Retrieve product variant info from session
        variant_id = session_data.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))

        try:
            variant = Varients.objects.get(id=variant_id)
        except Varients.DoesNotExist:
            messages.error(request, "Selected product variant does not exist.")
            return HttpResponseRedirect(reverse('productInfo', args=[pId]))

        if variant.stock >= quantity:
            user = request.user
            # Get or create the user's cart
            cart, created = Cart.objects.get_or_create(userId=user)

            # Check if the item already exists in the cart
            cart_item, created = CartItem.objects.get_or_create(
                productId=variant.product,
                varientId=variant,
                cartId=cart,
                defaults={'quantity': quantity}
            )

            if not created:
                # If the item already exists, update the quantity
                cart_item.quantity += quantity
                cart_item.save()

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
    productsList = Products.objects.all()
    sort = request.GET.get('sort')

    sizes = Size.objects.values('size').annotate(count=models.Count('size')).order_by('size')
    refreshRates = RefreshRate.objects.values('refreshRate').annotate(count=models.Count('refreshRate')).order_by('refreshRate')
    categories = Products.objects.values('category').annotate(count=models.Count('category')).order_by('category')
    productsList = productsList.annotate(min_price=Min('varient__price'))


    if sort == 'price_asc':
        productsList = productsList.order_by('-min_price')
    elif sort == 'price_desc':
        productsList = productsList.order_by('min_price')
    elif sort == 'new_arrivals':
        productsList = productsList.order_by('-createdAt')
    elif sort == 'az':
        productsList = productsList.order_by('name')
    elif sort == 'za':
        productsList = productsList.order_by('-name')


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
                        'stock': selectedVarient.stock,
                        'variantId': selectedVarient.id
                    })
                    
                    # Save the selected variant data to the session
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

    # For GET requests, return initial data
    session_data = request.session.get('product_data', None)
    if session_data:
        # If there's existing session data, use it
        context = {
            'product': product,
            'varientSize': varientSize,
            'varientRefreshRates': varientRefreshRates,
            'session_data': session_data
        }
    else:
        # If no session data, use default variant data
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
def orderDetails(request, oId):
    order = Order.objects.get(id=oId)

    orderItems = OrderItem.objects.filter(orderItemId=order)

    context = {
        'order': order,
        'orders': orderItems,
    }
    return render(request, 'orderDetails.html', context)

@never_cache
@login_required(login_url='/signIn')
def cancelOrder(request, oId):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=oId)

            order.orderStatus = 'canceled'
            order.save()

            return HttpResponseRedirect(reverse('order'))

        except Order.DoesNotExist:
            pass
        except OrderItem.DoesNotExist:
            pass

    return redirect('order')

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

    if request.method == 'POST':
        try:
            addressId = json.loads(request.body).get('selectedAddress')
            address = Address.objects.get(id=addressId)
            paymentMethod = json.loads(request.body).get('selectedPayment')
            finalOrderPrice = json.loads(request.body).get('finalOrderPrice')

            if not paymentMethod:
                messages.error(request, 'Please select a payment method.')
                errorData = {
                'message': 'No Payment Selected',
                'status': 'error',
                }
                return JsonResponse(errorData, status=400)
            
            characters = string.ascii_letters + string.digits
            orderNumber = ''.join(random.choice(characters) for _ in range(10))
            print("Order Id is " + orderNumber)

            order = Order.objects.create(
                userId=user,
                addressId=address,
                paymentMethod=paymentMethod,
                orderNo=orderNumber,
                totalPrice=finalOrderPrice
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
            responseData = {
                'message': 'Order Successfull',
                'status': 'success',
            }
            return JsonResponse(responseData, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)

    if request.session.get('show_error'):
        del request.session['show_error']

    context = {
        'products': cartItems,
        'addresses': addresses,
        'cart':carts
    }
    return render(request, 'checkout.html', context)