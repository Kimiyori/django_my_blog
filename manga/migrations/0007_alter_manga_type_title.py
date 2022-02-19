# Generated by Django 4.0.1 on 2022-02-08 17:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manga', '0006_remove_manga_title_text_delete_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manga',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manga', to='manga.mangatype'),
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_name', models.CharField(max_length=300)),
                ('russiam_name', models.CharField(max_length=300)),
                ('english_name', models.CharField(max_length=300)),
                ('manga', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='item', to='manga.manga')),
            ],
        ),
    ]