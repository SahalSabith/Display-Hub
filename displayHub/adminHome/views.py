from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from shopping.models import Order,OrderItem
from django.db.models import Count
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from django.db.models import Sum, F


# Create your views here.
@never_cache
@login_required(login_url='/admin/login')
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')

    filter_type = request.GET.get('filter_type', 'daily')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if filter_type == 'custom' and start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        orders = Order.objects.filter(orderedAt__date__range=[start_date, end_date])
    elif filter_type == 'weekly':
        one_week_ago = timezone.now().date() - timezone.timedelta(weeks=1)
        orders = Order.objects.filter(orderedAt__date__gte=one_week_ago)
    elif filter_type == 'monthly':
        one_month_ago = timezone.now().date() - timezone.timedelta(days=30)
        orders = Order.objects.filter(orderedAt__date__gte=one_month_ago)
    else:
        today = timezone.now().date()
        orders = Order.objects.filter(orderedAt__date=today)

    total_sales_count = orders.count()
    total_order_amount = sum(order.totalPrice for order in orders)

    # Calculate total discount
    total_discount = sum(
        sum((item.varientId.price * item.quantity) - item.totalPrice for item in order.orderItemId.all())
        for order in orders
    )

    # Calculate top selling products
    top_products = (
        OrderItem.objects.filter(orderItemId__in=orders)
        .values('productId__name', 'varientId__price')
        .annotate(
            sold_count=Sum('quantity'),
            revenue=Sum(F('quantity') * F('varientId__price'))  
        )
        .order_by('-sold_count')[:5]
    )

    context = {
        'orders': orders,
        'total_sales_count': total_sales_count,
        'total_order_amount': total_order_amount,
        'total_discount': total_discount,
        'filter_type': filter_type,
        'start_date': start_date,
        'end_date': end_date,
        'top_products': top_products,
    }
    return render(request, 'adminHome.html', context)

def generate_sales_report(request):
    # Get filter parameters
    filter_type = request.GET.get('filter_type', 'daily')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter orders based on parameters
    if filter_type == 'custom' and start_date and end_date:
        orders = Order.objects.filter(orderedAt__range=[start_date, end_date])
    elif filter_type == 'weekly':
        one_week_ago = timezone.now() - timezone.timedelta(weeks=1)
        orders = Order.objects.filter(orderedAt__gte=one_week_ago)
    elif filter_type == 'monthly':
        one_month_ago = timezone.now() - timezone.timedelta(days=30)
        orders = Order.objects.filter(orderedAt__gte=one_month_ago)
    else:
        today = timezone.now().date()
        orders = Order.objects.filter(orderedAt__date=today)

    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Create the PDF object using reportlab
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Add title
    styles = getSampleStyleSheet()
    elements.append(Paragraph(" Display Hub Sales Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Add date range information
    if filter_type == 'custom':
        date_info = f"Custom Range: {start_date} to {end_date}"
    elif filter_type == 'weekly':
        date_info = "Last Week"
    elif filter_type == 'monthly':
        date_info = "Last Month"
    else:
        date_info = "Today"
    elements.append(Paragraph(date_info, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Create table data
    data = [['Order ID', 'Customer', 'Total Amount', 'Discounts','Order Date']]
    for order in orders:
        data.append([
            str(order.orderNo),
            order.userId.get_full_name(),
            f"₹{order.totalPrice:.2f}",
            f"₹{order.discountPrice}",
            order.orderedAt.strftime('%Y-%m-%d %H:%M')
        ])

    # Create table
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    elements.append(table)

    elements.append(Spacer(1, 24))
    total_sales = sum(order.totalPrice for order in orders)
    elements.append(Paragraph(f"Total Sales: ${total_sales:.2f}", styles['Heading2']))
    elements.append(Paragraph(f"Number of Orders: {orders.count()}", styles['Normal']))

    doc.build(elements)
    return response

@never_cache
@login_required(login_url='/admin/login')
def allUsers(request):
    if not request.user.is_superuser:
        return redirect('home')
    allUsers = User.objects.all().order_by('-id')
    return render(request,'users.html',{'allUsers':allUsers})