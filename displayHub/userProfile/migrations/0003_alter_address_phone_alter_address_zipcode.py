# Generated by Django 5.1 on 2024-09-05 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userProfile', '0002_alter_address_phone_alter_address_zipcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='phone',
            field=models.CharField(),
        ),
        migrations.AlterField(
            model_name='address',
            name='zipCode',
            field=models.CharField(),
        ),
    ]
