from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404,HttpResponse
from decouple import config
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from shopping.models import Cart,CartItem,OrderItem,Order
import razorpay
from django.db import transaction
from userProfile.models import Address
from django.core.exceptions import ObjectDoesNotExist
from discounts.models import Coupon,CouponUsage
from datetime import datetime
from django.contrib import messages
import json
from django.http import JsonResponse
import string
import random
from userProfile.models import Wallet,Transaction
from adminManagements.models import Products,Varients
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from webpush import send_user_notification
import logging
logger = logging.getLogger(__name__)

# Create your views here.
RAZOR_KEY_ID = config('RAZOR_KEY_ID')
RAZOR_KEY_SECRET = config('RAZOR_KEY_SECRET')

@never_cache
@login_required(login_url='/signIn')
def checkOut(request):
    userId = request.user
    addresses = Address.objects.filter(userId=userId)
    try:    
        cart = Cart.objects.get(userId=userId)
    except ObjectDoesNotExist:
        return redirect('cart')
    cartItems = CartItem.objects.filter(cartId=cart).count()
    request.session['cartCount'] = cartItems
    try:
        cart = Cart.objects.get(userId=userId)
    except ObjectDoesNotExist:
        return redirect('cart')
    cart_items = CartItem.objects.filter(cartId=cart).order_by('-id')
    
    for Item in cart_items:
        if Item.productId.status == False:
            itemId = Item.pk
            messages.warning(request,f'{Item.productId.name} is unavailable now')
            deleteItem = CartItem.objects.get(id=itemId).delete()
        elif Item.varientId.stock <= 0:
            itemId = Item.pk
            messages.warning(request,f'{Item.productId.name} is Out Of Stock now')
            deleteItem = CartItem.objects.get(id=itemId).delete()

    coupon = Coupon.objects.all()

    for coupon in coupon:
        if coupon.validTo < datetime.now().date():
            coupon.status = False
            coupon.save()

    coupons = Coupon.objects.filter(status=True).exclude(
    id__in=CouponUsage.objects.values_list('coupon_id', flat=True))

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

            if payment_method == 'wallet':
                wallet = Wallet.objects.get(userId=userId)
                if wallet.balance < float(final_order_price):
                    return JsonResponse({'message': 'Insufficient wallet balance', 'status': 'error'}, status=400)
                order_status = 'dispatched'
            elif payment_method == 'internetBanking':
                order_status = 'FAILURE'
            elif payment_method == 'cashOnDelivery':
                if final_order_price < 1000:
                    return JsonResponse({'message': 'The order amount should be more than 1000 for cash on delivery.', 'status': 'error'}, status=400)
                order_status = 'dispatched'
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

                productAmount = item.varientId.price
                offerAmount = item.price

                discountedPrice = productAmount - offerAmount

                order.discountPrice = order.discountPrice+discountedPrice
                order.save()
            
            payload = {
                'head': 'New Order',
                'body': 'A new order has been placed!',
                'url': f'/account/orderDetails/{order_number}/'
            }

            logger.info(f"Sending notification to user {request.user.username}")
            send_user_notification(user=request.user, payload=payload, ttl=1000)
            logger.info("Notification sent")

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
                    'callback_url': 'https://displayhub.store/razorpay/callback/',
                    'order_name': order_number,
                    'final_order_price': final_order_price
                }
                return JsonResponse(response_data, status=200)

            # Return success for non-Razorpay payment method
            return JsonResponse({'message': 'Order Successful', 'status': 'success'}, status=200)

        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)

    context = {'products': cart_items, 'addresses': addresses, 'cart': cart, 'coupons': coupons}
    return render(request, 'checkout.html', context)

@login_required
def get_wallet_balance(request):
    wallet, created = Wallet.objects.get_or_create(userId=request.user)
    return JsonResponse({'balance': wallet.balance})

@require_POST
@login_required
@transaction.atomic
def process_wallet_payment(request):
    data = json.loads(request.body)
    final_order_price = float(data.get('finalOrderPrice'))
    
    wallet = Wallet.objects.get(userId=request.user)
    
    if wallet.balance < final_order_price:
        return JsonResponse({'status': 'error', 'message': 'Insufficient balance'}, status=400)
    
    # Deduct the amount from the wallet
    wallet.balance -= final_order_price
    wallet.save()
    
    # Create a transaction record
    Transaction.objects.create(
        walletId=wallet,
        transactionType='addMoney',
        amount=-final_order_price  # Negative amount for deduction
    )
    # Update the order status
    order = Order.objects.filter(userId=request.user).latest('orderedAt')
    order.orderStatus = 'dispatched'
    order.save()
    
    return JsonResponse({'status': 'success', 'message': 'Payment processed successfully'})


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
            order.pamentId = payment_id
            order.signatreId = signature_id

            # Verify the signature
            if verify_signature(request.POST):
                # Signature is valid, mark payment as successful
                order.orderStatus = "dispatched"
                order.save()
                return render(request, "callback.html", context={"status": "success"})
            else:
                # Invalid signature, mark payment as failed
                order.orderStatus = "FAILURE"
                order.save()
                return render(request, "callback.html", context={"status": "failure"})
        else:
            # Handle Razorpay error response
            error_metadata = json.loads(request.POST.get("error[metadata]"))
            payment_id = error_metadata.get("payment_id", "")
            provider_order_id = error_metadata.get("order_id", "")

            # Fetch the corresponding order
            order = Order.objects.get(provider_order_id=provider_order_id)
            order.pamentId = payment_id
            order.orderStatus = "FAILURE"
            order.save()

            return render(request, "callback.html", context={"status": "failure"})

    return render(request, "callback.html", context={"status": "error"})


@never_cache
@login_required(login_url='/signIn')
def repayment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('orderId')
            
            order = Order.objects.get(id=order_id)
            
            if order.orderStatus != 'FAILURE':
                return JsonResponse({'message': 'This order does not require repayment', 'status': 'error'}, status=400)
            
            # Create a new Razorpay order
            client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
            razorpay_order = client.order.create({
                "amount": int(order.totalPrice) * 100,
                "currency": "INR",
                "payment_capture": "1"
            })
            
            # Update the order with the new Razorpay order ID
            order.provider_order_id = razorpay_order['id']
            order.save()
            
            response_data = {
                'message': 'Repayment Initiated',
                'status': 'success',
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': RAZOR_KEY_ID,
                'callback_url': 'https://displayhub.store/razorpay/callback/',
                'order_name': order.orderNo,
                'final_order_price': order.totalPrice
            }
            return JsonResponse(response_data, status=200)
        
        except Exception as e:
            return JsonResponse({'message': str(e), 'status': 'error'}, status=500)
    
    return JsonResponse({'message': 'Invalid request method', 'status': 'error'}, status=405)


def orderSuccess(request):

    return render(request,'paymentSuccess.html')


@never_cache
@login_required(login_url='/signIn')
def create_razorpay_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            phone = data.get('phone')

            # Create a new Razorpay order
            client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
            razorpay_order = client.order.create({
                "amount": int(amount) * 100,  # Convert to paise
                "currency": "INR",
                "payment_capture": "1"
            })
            
            response_data = {
                'message': 'Order Created',
                'status': 'success',
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': RAZOR_KEY_ID,
                'final_order_price': amount
            }
            return JsonResponse(response_data, status=200)
        
        except Exception as e:
            return JsonResponse({'message': str(e), 'status': 'error'}, status=500)
    
    return JsonResponse({'message': 'Invalid request method', 'status': 'error'}, status=405)


@never_cache
@login_required(login_url='/signIn')
def credit_wallet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_id = data.get('paymentId')
            amount = data.get('amount')
            phone = data.get('phone')

            # Get the user's wallet
            wallet = Wallet.objects.get(userId=request.user)

            # Update wallet balance
            wallet.balance += float(amount)  # Make sure to handle the amount correctly
            wallet.save()

            # Log the transaction
            Transaction.objects.create(
                walletId=wallet,
                transactionType='addMoney',
                amount=float(amount)
            )

            return JsonResponse({'message': 'Money added to wallet successfully!', 'status': 'success'}, status=200)

        except Exception as e:
            return JsonResponse({'message': str(e), 'status': 'error'}, status=500)

    return JsonResponse({'message': 'Invalid request method', 'status': 'error'}, status=405)
