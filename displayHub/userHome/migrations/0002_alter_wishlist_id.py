# Generated by Django 5.1 on 2024-09-27 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userHome', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
