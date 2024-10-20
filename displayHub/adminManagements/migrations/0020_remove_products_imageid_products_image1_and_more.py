# Generated by Django 5.1 on 2024-09-11 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminManagements', '0019_alter_products_refreshrate_alter_products_resolution_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='imageId',
        ),
        migrations.AddField(
            model_name='products',
            name='image1',
            field=models.ImageField(blank=True, null=True, upload_to='media/'),
        ),
        migrations.AddField(
            model_name='products',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to='media/'),
        ),
        migrations.AddField(
            model_name='products',
            name='image3',
            field=models.ImageField(blank=True, null=True, upload_to='media/'),
        ),
        migrations.AddField(
            model_name='products',
            name='image4',
            field=models.ImageField(blank=True, null=True, upload_to='media/'),
        ),
        migrations.DeleteModel(
            name='ProductImage',
        ),
    ]
