# Generated by Django 5.1 on 2024-09-11 05:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0009_alter_order_orderstatus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='product',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='product',
        ),
    ]
