# Generated by Django 4.0.1 on 2022-07-12 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0002_urls_alter_anime_title_alter_manga_demographic_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='anime',
            name='score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='manga',
            name='score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
    ]
