# Generated by Django 5.1 on 2024-09-11 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminManagements', '0021_remove_products_refreshrate_remove_products_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='varients',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
