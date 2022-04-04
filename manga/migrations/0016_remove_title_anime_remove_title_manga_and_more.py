# Generated by Django 4.0.1 on 2022-02-26 18:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('manga', '0015_title_anime'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='title',
            name='anime',
        ),
        migrations.RemoveField(
            model_name='title',
            name='manga',
        ),
        migrations.AddField(
            model_name='title',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='title', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='title',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]