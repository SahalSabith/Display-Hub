from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from shopping.models import Order,OrderItem
from django.db.models import Count
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# Create your views here.
@never_cache
@login_required(login_url='/admin/login')
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')

    # Get the date filter parameters
    filter_type = request.GET.get('filter_type', 'daily')  # Default to daily
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if filter_type == 'custom' and start_date and end_date:
        # Filter by custom date range
        orders = Order.objects.filter(orderedAt__range=[start_date, end_date])
    elif filter_type == 'weekly':
        # Filter by the last week
        one_week_ago = timezone.now() - timezone.timedelta(weeks=1)
        orders = Order.objects.filter(orderedAt__gte=one_week_ago)
    elif filter_type == 'monthly':
        # Filter by the last month
        one_month_ago = timezone.now() - timezone.timedelta(days=30)
        orders = Order.objects.filter(orderedAt__gte=one_month_ago)
    else:
        # Default to daily
        today = timezone.now().date()
        orders = Order.objects.filter(orderedAt__date=today)

    # Calculate totals
    total_sales_count = orders.count()
    total_order_amount = sum(order.totalPrice for order in orders)

    # Calculate total discount
    total_discount = 0
    for order in orders:
        order_items = order.orderItemId.all()  # Fetch related order items
        for item in order_items:
            original_price = item.varientId.price  # Get the price from the variant
            # Calculate discount: original price minus the total price for this item
            discount_per_item = (original_price * item.quantity) - item.totalPrice
            total_discount += discount_per_item

    context = {
        'orders': orders,
        'total_sales_count': total_sales_count,
        'total_order_amount': total_order_amount,
        'total_discount': total_discount,
        'filter_type': filter_type,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'adminHome.html', context)

def generate_sales_report(request):
    # Create a HttpResponse object with PDF header
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Create a PDF object and set up the canvas
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 50, "Sales Report")

    # Column Headers
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, height - 100, "Order ID")
    pdf.drawString(250, height - 100, "Customer")
    pdf.drawString(400, height - 100, "Total Amount")

    # Add Sales Data
    pdf.setFont("Helvetica", 12)
    y_position = height - 120
    sales = Order.objects.all()  # Adjust this queryset as needed

    for sale in sales:
        pdf.drawString(100, y_position, str(sale.orderNo))
        pdf.drawString(250, y_position, sale.userId.first_name)  # Adjust based on your Sale model
        pdf.drawString(400, y_position, f"₹{sale.totalPrice:.2f}")  # Adjust based on your Sale model
        y_position -= 20  # Move down for the next entry

    # Finalize the PDF and send it to the client
    pdf.showPage()
    pdf.save()
    
    return response

@never_cache
@login_required(login_url='/admin/login')
def allUsers(request):
    if not request.user.is_superuser:
        return redirect('home')
    allUsers = User.objects.all().order_by('-id')
    return render(request,'users.html',{'allUsers':allUsers})