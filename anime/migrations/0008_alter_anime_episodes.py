# Generated by Django 4.0.1 on 2022-01-10 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anime', '0007_anime_image_studio_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anime',
            name='episodes',
            field=models.IntegerField(),
        ),
    ]
