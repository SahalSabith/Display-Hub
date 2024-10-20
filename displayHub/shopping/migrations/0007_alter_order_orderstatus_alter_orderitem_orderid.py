# Generated by Django 5.1 on 2024-09-06 05:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0006_order_totalprice_orderitem_totalprice_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='orderStatus',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered'), ('Canceled', 'Canceled'), ('Returned', 'Returned'), ('Refunded', 'Refunded'), ('Failed', 'Failed'), ('On Hold', 'On Hold'), ('Completed', 'Completed'), ('Awaiting Payment', 'Awaiting Payment')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='orderId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderId', to='shopping.order'),
        ),
    ]
