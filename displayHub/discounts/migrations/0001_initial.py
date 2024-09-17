# Generated by Django 5.1 on 2024-09-17 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('adminManagements', '0024_alter_varients_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('couponCode', models.CharField(max_length=40, unique=True)),
                ('validFrom', models.DateField()),
                ('validTo', models.DateField()),
                ('discountType', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed')])),
                ('discountValue', models.FloatField()),
                ('minPurchaseAmount', models.FloatField()),
                ('maxDiscountAmount', models.FloatField()),
                ('usageLimit', models.IntegerField()),
                ('usedCount', models.IntegerField()),
                ('status', models.BooleanField(default=True)),
                ('applicableBrand', models.ManyToManyField(related_name='coupon', to='adminManagements.brand')),
                ('applicableCategory', models.ManyToManyField(related_name='coupon', to='adminManagements.category')),
                ('applicableProducts', models.ManyToManyField(related_name='coupon', to='adminManagements.products')),
            ],
        ),
    ]
