# Generated by Django 5.1 on 2024-09-05 10:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminManagements', '0012_remove_productimage_croppedimage1_and_more'),
        ('shopping', '0004_alter_cartitem_product'),
        ('userProfile', '0003_alter_address_phone_alter_address_zipcode'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orderStatus', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'), ('canceled', 'Canceled'), ('returned', 'Returned'), ('refunded', 'Refunded'), ('failed', 'Failed'), ('on_hold', 'On Hold'), ('completed', 'Completed'), ('awaiting_payment', 'Awaiting Payment')], default='pending', max_length=20)),
                ('orderedAt', models.DateTimeField(auto_now=True)),
                ('paymentMethod', models.CharField(choices=[('cashOnDelivery', 'CashOnDelivey'), ('Wallet', 'Wallet'), ('internetBanking', 'InternetBanking')], default='cashOnDelivery', max_length=20)),
                ('orderNo', models.CharField(max_length=255, unique=True)),
                ('addressId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userProfile.address')),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('orderId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopping.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminManagements.varients')),
            ],
        ),
    ]
