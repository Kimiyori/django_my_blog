# Generated by Django 4.0.1 on 2022-03-14 16:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0026_rename_content_file_file_rename_content_image_image_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='url',
            new_name='video',
        ),
    ]