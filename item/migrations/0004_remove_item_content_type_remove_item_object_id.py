# Generated by Django 4.0.1 on 2022-01-12 14:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0003_alter_item_content_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='item',
            name='object_id',
        ),
    ]