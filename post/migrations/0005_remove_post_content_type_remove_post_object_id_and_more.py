# Generated by Django 4.0.1 on 2022-03-01 15:01

from django.db import migrations, models
import django.db.models.deletion
import post.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('post', '0004_post_content_type_post_object_id_video_text_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='post',
            name='object_id',
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('order', post.fields.OrderField(blank=True)),
                ('content_type', models.ForeignKey(limit_choices_to={'model__in': ('text', 'video', 'image', 'file')}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='post.post')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]