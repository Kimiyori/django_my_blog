# Generated by Django 4.0.1 on 2022-02-08 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manga', '0008_alter_title_english_name_alter_title_original_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='title',
            old_name='russiam_name',
            new_name='russian_name',
        ),
    ]