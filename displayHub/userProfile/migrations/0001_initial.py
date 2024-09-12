# Generated by Django 5.1 on 2024-09-05 06:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField()),
                ('phone', models.IntegerField(max_length=10)),
                ('houseName', models.CharField()),
                ('city', models.CharField()),
                ('district', models.CharField()),
                ('state', models.CharField()),
                ('zipCode', models.IntegerField(max_length=6)),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
