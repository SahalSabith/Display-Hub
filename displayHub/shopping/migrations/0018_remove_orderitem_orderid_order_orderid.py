# Generated by Django 5.1 on 2024-09-14 16:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0017_remove_order_orderid_orderitem_orderid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='orderId',
        ),
        migrations.AddField(
            model_name='order',
            name='orderId',
            field=models.ForeignKey(default=123, on_delete=django.db.models.deletion.CASCADE, related_name='orderItemId', to='shopping.orderitem'),
        ),
    ]
