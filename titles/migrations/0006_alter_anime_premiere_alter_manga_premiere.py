# Generated by Django 4.0.1 on 2022-07-18 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0005_alter_anime_urls_alter_manga_urls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anime',
            name='premiere',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='manga',
            name='premiere',
            field=models.DateField(blank=True, null=True),
        ),
    ]