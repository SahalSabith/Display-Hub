# Generated by Django 5.1 on 2024-08-24 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminManagements', '0006_alter_varients_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
