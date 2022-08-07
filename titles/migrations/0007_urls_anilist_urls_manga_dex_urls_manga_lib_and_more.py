# Generated by Django 4.0.1 on 2022-08-06 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0006_alter_anime_premiere_alter_manga_premiere'),
    ]

    operations = [
        migrations.AddField(
            model_name='urls',
            name='anilist',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='urls',
            name='manga_dex',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='urls',
            name='manga_lib',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='urls',
            name='manga_updates',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='urls',
            name='shiki',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='urls',
            name='world_art',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='urls',
            name='mal',
            field=models.URLField(blank=True, null=True),
        ),
    ]
