# Generated by Django 5.1 on 2024-10-07 04:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groupmessage',
            options={'ordering': ['-created']},
        ),
        migrations.RenameField(
            model_name='groupmessage',
            old_name='createdAt',
            new_name='created',
        ),
    ]
