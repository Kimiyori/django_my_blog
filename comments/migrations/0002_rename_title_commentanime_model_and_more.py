# Generated by Django 4.0.1 on 2022-08-07 18:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("comments", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="commentanime",
            old_name="title",
            new_name="model",
        ),
        migrations.RenameField(
            model_name="commentmanga",
            old_name="title",
            new_name="model",
        ),
        migrations.RenameField(
            model_name="commentpost",
            old_name="post",
            new_name="model",
        ),
    ]
