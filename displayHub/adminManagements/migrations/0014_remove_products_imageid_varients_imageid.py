# Generated by Django 5.1 on 2024-09-11 05:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminManagements', '0013_remove_varients_imageid_products_imageid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='imageId',
        ),
        migrations.AddField(
            model_name='varients',
            name='imageId',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminManagements.productimage'),
        ),
    ]
