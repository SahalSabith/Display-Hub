# Generated by Django 5.1 on 2024-09-11 05:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminManagements', '0016_alter_products_refreshrate_alter_products_resolution_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='refreshRate',
        ),
        migrations.RemoveField(
            model_name='products',
            name='size',
        ),
        migrations.RemoveField(
            model_name='products',
            name='imageId',
        ),
        migrations.RemoveField(
            model_name='products',
            name='resolution',
        ),
        migrations.RemoveField(
            model_name='products',
            name='status',
        ),
        migrations.CreateModel(
            name='Varients',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('price', models.FloatField()),
                ('size', models.IntegerField()),
                ('stock', models.IntegerField()),
                ('resolution', models.IntegerField()),
                ('refreshRate', models.IntegerField()),
                ('status', models.BooleanField(default=True)),
                ('imageId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminManagements.productimage')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='adminManagements.products')),
            ],
        ),
        migrations.DeleteModel(
            name='RefreshRate',
        ),
        migrations.DeleteModel(
            name='Size',
        ),
    ]
