# Generated by Django 5.1 on 2024-09-14 16:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0020_remove_order_orderid_order_orderitemid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='orderItemId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopping.orderitem'),
        ),
    ]
