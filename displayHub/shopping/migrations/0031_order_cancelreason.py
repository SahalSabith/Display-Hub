# Generated by Django 5.1 on 2024-09-15 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0030_alter_orderitem_orderitemid'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cancelReason',
            field=models.TextField(default=1901),
        ),
    ]
