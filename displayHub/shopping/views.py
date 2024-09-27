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
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

RAZOR_KEY_ID = config('RAZOR_KEY_ID')
RAZOR_KEY_SECRET = config('RAZOR_KEY_SECRET')

@never_cache
@login_required(login_url='/signIn')
def cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(userId=user)
    cartItems = CartItem.objects.filter(cartId=cart).order_by('-id')
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

@never_cache
@login_required(login_url='/signIn')
def checkOut(request):
    userId = request.user
    addresses = Address.objects.filter(userId=userId)
    try:
        cart = Cart.objects.get(userId=userId)
    except ObjectDoesNotExist:
        return redirect('cart')
    cart_items = CartItem.objects.filter(cartId=cart).order_by('-id')
    coupon = Coupon.objects.all()

    for coupon in coupon:
        if coupon.validTo < datetime.now().date():
            coupon.status = False
            coupon.save()

    coupons = Coupon.objects.filter(status=True)

    if not cart_items.exists():
        messages.error(request, 'Please add items to the cart')
        return redirect('cart')

    if request.method == 'POST':
        try:
            # Get address and payment information
            data = json.loads(request.body)
            addressId = data.get('selectedAddress')
            address = Address.objects.get(id=addressId)
            payment_method = data.get('selectedPayment')
            final_order_price = data.get('finalOrderPrice')

            # Razorpay payment integration for 'internetBanking'
            razorpay_order = None
            if payment_method == 'internetBanking':
                client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
                razorpay_order = client.order.create(
                    {"amount": int(final_order_price) * 100, "currency": "INR", "payment_capture": "1"}
                )

            if not payment_method:
                messages.error(request, 'Please select a payment method.')
                return JsonResponse({'message': 'No Payment Selected', 'status': 'error'}, status=400)

            # Generate a random order number
            characters = string.ascii_letters + string.digits
            order_number = ''.join(random.choice(characters) for _ in range(10))

            if payment_method == 'internetBanking':
                order_status = 'FAILURE'
            else:
                order_status = 'dispatched' 

            order = Order.objects.create(
                userId=userId,
                addressId=address,
                paymentMethod=payment_method,
                orderNo=order_number,
                totalPrice=final_order_price,
                orderStatus=order_status,
                provider_order_id=razorpay_order['id'] if razorpay_order else None 
            )


            # Create order items and update stock
            for item in cart_items:
                product = Products.objects.get(id=item.productId.id)
                variant = Varients.objects.get(id=item.varientId.id)
                OrderItem.objects.create(
                    orderItemId=order,
                    productId=product,
                    varientId=variant,
                    quantity=item.quantity,
                    totalPrice=item.cartItemTotal()
                )
                variant.stock -= item.quantity
                variant.save()

            # Clear cart after order is placed
            cart_items.delete()
            cart.delete()

            # Prepare data for Razorpay payment page if payment method is Razorpay
            if payment_method == 'internetBanking':
                response_data = {
                    'message': 'Order Successful',
                    'status': 'success',
                    'selectedAddress':address.phone,
                    'razorpay_order_id': razorpay_order['id'],
                    'razorpay_key': RAZOR_KEY_ID,
                    'callback_url': 'http://127.0.0.1:8000/razorpay/callback/',
                    'order_name': order_number,
                    'final_order_price': final_order_price
                }
                return JsonResponse(response_data, status=200)

            # Return success for non-Razorpay payment method
            return JsonResponse({'message': 'Order Successful', 'status': 'success'}, status=200)

        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)

    context = {'products': cart_items, 'addresses': addresses, 'cart': cart,'coupons':coupons}
    return render(request, 'checkout.html', context)



@csrf_exempt
def razorpay_callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(response_data)
            return True
        except:
            return False

    if request.method == "POST":
        if "razorpay_signature" in request.POST:
            # Extract Razorpay details from POST request
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")

            # Fetch the corresponding order in your system
            order = Order.objects.get(provider_order_id=provider_order_id)
            order.payment_id = payment_id
            order.signature_id = signature_id

            # Verify the signature
            if verify_signature(request.POST):
                # Signature is valid, mark payment as successful
                order.order_status = "SUCCESS"
                order.save()
                return render(request, "callback.html", context={"status": "success"})
            else:
                # Invalid signature, mark payment as failed
                order.order_status = "FAILURE"
                order.save()
                return render(request, "callback.html", context={"status": "failure"})
        else:
            # Handle Razorpay error response
            error_metadata = json.loads(request.POST.get("error[metadata]"))
            payment_id = error_metadata.get("payment_id", "")
            provider_order_id = error_metadata.get("order_id", "")

            # Fetch the corresponding order
            order = Order.objects.get(provider_order_id=provider_order_id)
            order.payment_id = payment_id
            order.order_status = "FAILURE"
            order.save()

            return render(request, "callback.html", context={"status": "failure"})

    return render(request, "callback.html", context={"status": "error"})