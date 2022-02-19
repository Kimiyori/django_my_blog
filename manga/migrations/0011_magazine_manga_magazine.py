# Generated by Django 4.0.1 on 2022-02-12 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manga', '0010_alter_title_manga'),
    ]

    operations = [
        migrations.CreateModel(
            name='Magazine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('slug', models.SlugField(default='', max_length=150)),
            ],
        ),
        migrations.AddField(
            model_name='manga',
            name='magazine',
            field=models.ManyToManyField(blank=True, related_name='manga', to='manga.Magazine'),
        ),
    ]