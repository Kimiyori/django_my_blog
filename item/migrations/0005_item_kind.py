# Generated by Django 4.0.1 on 2022-01-12 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kind', '0001_initial'),
        ('item', '0004_remove_item_content_type_remove_item_object_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='kind',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='kind', to='kind.kind'),
        ),
    ]