# Generated by Django 5.1 on 2024-08-23 06:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminManagements', '0002_brand_staus_products_staus_varients_staus'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brand',
            old_name='staus',
            new_name='status',
        ),
        migrations.RenameField(
            model_name='products',
            old_name='staus',
            new_name='status',
        ),
        migrations.RenameField(
            model_name='varients',
            old_name='staus',
            new_name='status',
        ),
    ]
