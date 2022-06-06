# Generated by Django 4.0.1 on 2022-06-06 06:40

from django.db import migrations, models
import django.db.models.deletion
import titles.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Anime',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('premiere', models.DateField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('episodes', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='AnimeType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('slug', models.SlugField(default='', max_length=250)),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Authors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='AuthorTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('pseudonym', models.CharField(blank=True, max_length=200, null=True)),
                ('photo', models.ImageField(blank=True, upload_to='authors/')),
            ],
        ),
        migrations.CreateModel(
            name='Demographic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('slug', models.SlugField(default='', max_length=250)),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('slug', models.SlugField(default='', max_length=250)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image', models.ImageField(blank=True, max_length=300, upload_to=titles.models.image_path)),
                ('thumbnail', models.ImageField(blank=True, max_length=300, upload_to=titles.models.image_thumb_path)),
            ],
        ),
        migrations.CreateModel(
            name='Magazine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, upload_to='magazines/')),
                ('slug', models.SlugField(default='', max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Manga',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('premiere', models.DateField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('volumes', models.IntegerField(blank=True, null=True)),
                ('chapters', models.IntegerField(blank=True, null=True)),
                ('authors', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manga', to='titles.authors')),
                ('demographic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manga', to='titles.demographic')),
                ('genre', models.ManyToManyField(blank=True, related_name='%(class)s', to='titles.Genre')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s', to='titles.image')),
                ('magazine', models.ManyToManyField(blank=True, related_name='manga', to='titles.Magazine')),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='MangaType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('slug', models.SlugField(default='', max_length=250)),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, upload_to='publishers/')),
                ('slug', models.SlugField(default='', max_length=250)),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Studio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, upload_to='studios/')),
                ('slug', models.SlugField(default='', max_length=250)),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('slug', models.SlugField(default='', max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_name', models.CharField(blank=True, max_length=300, null=True)),
                ('russian_name', models.CharField(blank=True, max_length=300, null=True)),
                ('english_name', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SequelPrequelManga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prequel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sequel', to='titles.manga')),
                ('sequel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prequel', to='titles.manga')),
            ],
        ),
        migrations.CreateModel(
            name='SequelPrequelAnime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prequel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sequel', to='titles.anime')),
                ('sequel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prequel', to='titles.anime')),
            ],
        ),
        migrations.AddField(
            model_name='manga',
            name='publisher',
            field=models.ManyToManyField(blank=True, related_name='manga', to='titles.Publisher'),
        ),
        migrations.AddField(
            model_name='manga',
            name='related_post',
            field=models.ManyToManyField(blank=True, related_name='%(class)s', to='post.Post'),
        ),
        migrations.AddField(
            model_name='manga',
            name='theme',
            field=models.ManyToManyField(blank=True, related_name='%(class)s', to='titles.Theme'),
        ),
        migrations.AddField(
            model_name='manga',
            name='title',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s', to='titles.title'),
        ),
        migrations.AddField(
            model_name='manga',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manga', to='titles.mangatype'),
        ),
        migrations.AddField(
            model_name='authors',
            name='artist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='authors_artist', to='titles.authortable'),
        ),
        migrations.AddField(
            model_name='authors',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='authors_author', to='titles.authortable'),
        ),
        migrations.AddField(
            model_name='anime',
            name='genre',
            field=models.ManyToManyField(blank=True, related_name='%(class)s', to='titles.Genre'),
        ),
        migrations.AddField(
            model_name='anime',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s', to='titles.image'),
        ),
        migrations.AddField(
            model_name='anime',
            name='related_post',
            field=models.ManyToManyField(blank=True, related_name='%(class)s', to='post.Post'),
        ),
        migrations.AddField(
            model_name='anime',
            name='studio',
            field=models.ManyToManyField(blank=True, related_name='anime', to='titles.Studio'),
        ),
        migrations.AddField(
            model_name='anime',
            name='theme',
            field=models.ManyToManyField(blank=True, related_name='%(class)s', to='titles.Theme'),
        ),
        migrations.AddField(
            model_name='anime',
            name='title',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s', to='titles.title'),
        ),
        migrations.AddField(
            model_name='anime',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='anime', to='titles.animetype'),
        ),
        migrations.CreateModel(
            name='AdaptationReverse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adaptation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='based_on', to='titles.manga')),
                ('based_on', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='adaptation', to='titles.anime')),
            ],
        ),
        migrations.CreateModel(
            name='Adaptation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adaptation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='based_on', to='titles.anime')),
                ('based_on', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='adaptation', to='titles.manga')),
            ],
        ),
        migrations.AddIndex(
            model_name='manga',
            index=models.Index(fields=['id'], name='titles_mang_id_27add6_idx'),
        ),
        migrations.AddIndex(
            model_name='anime',
            index=models.Index(fields=['id'], name='titles_anim_id_54c1ae_idx'),
        ),
    ]
