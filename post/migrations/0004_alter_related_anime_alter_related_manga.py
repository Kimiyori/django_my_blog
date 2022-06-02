# Generated by Django 4.0.1 on 2022-05-27 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0006_alter_anime_options_alter_manga_options_and_more'),
        ('post', '0003_alter_video_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='related',
            name='anime',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related', to='titles.anime'),
        ),
        migrations.AlterField(
            model_name='related',
            name='manga',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related', to='titles.manga'),
        ),
    ]
