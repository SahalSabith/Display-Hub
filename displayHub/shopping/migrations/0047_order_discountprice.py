# Generated by Django 5.1 on 2024-10-01 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0046_remove_order_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discountPrice',
            field=models.IntegerField(default=0),
        ),
    ]
