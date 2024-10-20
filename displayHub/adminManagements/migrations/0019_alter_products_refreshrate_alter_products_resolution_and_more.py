# Generated by Django 5.1 on 2024-09-11 06:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminManagements', '0018_refreshrate_size_products_imageid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='refreshRate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminManagements.refreshrate'),
        ),
        migrations.AlterField(
            model_name='products',
            name='resolution',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='products',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminManagements.size'),
        ),
    ]
