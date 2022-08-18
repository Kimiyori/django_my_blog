from io import BytesIO
from django.db import models
import uuid
from django.urls import reverse
from django.core.files.base import ContentFile
from PIL import Image as PILImage
# Create your models here.


class Demographic(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self) -> str:
        return str(self.name)


class Genre(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return str(self.name)


class Publisher(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='publishers/', blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self) -> str:
        return str(self.name)


class MangaType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self) -> str:
        return str(self.name)


class AuthorTable(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    pseudonym = models.CharField(max_length=200, null=True, blank=True)
    photo = models.ImageField(upload_to='authors/', blank=True)

    def __str__(self) -> str:
        return str(self.name)


class Authors(models.Model):
    author = models.ForeignKey(AuthorTable, on_delete=models.CASCADE,
                               related_name='authors_author', null=True, blank=True)
    artist = models.ForeignKey(AuthorTable, on_delete=models.CASCADE,
                               related_name='authors_artist', null=True, blank=True)

    def __str__(self) -> str:
        return f'Author-{self.author} Artist-{self.artist}'


class Theme(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=150, default='')

    def __str__(self) -> str:
        return str(self.name)


class Magazine(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='magazines/', blank=True)
    slug = models.SlugField(max_length=150, default='')

    def __str__(self) -> str:
        return str(self.name)


class Title(models.Model):

    original_name = models.CharField(max_length=300, null=True, blank=True)
    russian_name = models.CharField(max_length=300, null=True, blank=True)
    english_name = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self) -> str:
        if self.original_name:
            return self.original_name
        elif self.english_name:
            return self.english_name
        elif self.russian_name:
            return self.russian_name
        else:
            return "Name does not exist"


class AnimeType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self) -> str:
        return str(self.name)


class Studio(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='studios/', blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self) -> str:
        return str(self.name)


class Adaptation(models.Model):
    adaptation = models.ForeignKey('Anime', on_delete=models.CASCADE,
                                   related_name='based_on', null=True, blank=True)
    based_on = models.ForeignKey('Manga', on_delete=models.CASCADE,
                                 related_name='adaptation', null=True, blank=True)


class AdaptationReverse(models.Model):
    adaptation = models.ForeignKey('Manga', on_delete=models.CASCADE,
                                   related_name='based_on', null=True, blank=True)
    based_on = models.ForeignKey('Anime', on_delete=models.CASCADE,
                                 related_name='adaptation', null=True, blank=True)


class SequelPrequelAnime(models.Model):
    sequel = models.ForeignKey('Anime', on_delete=models.CASCADE,
                               related_name='prequel', null=True, blank=True)
    prequel = models.ForeignKey('Anime', on_delete=models.CASCADE,
                                related_name='sequel', null=True, blank=True)


class SequelPrequelManga(models.Model):
    sequel = models.ForeignKey('Manga', on_delete=models.CASCADE,
                               related_name='prequel', null=True, blank=True)
    prequel = models.ForeignKey('Manga', on_delete=models.CASCADE,
                                related_name='sequel', null=True, blank=True)


def image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'{instance._meta.model_name}/{instance.id}/original/{filename}'


def image_thumb_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'{instance._meta.model_name}/{instance.id}/thumbnail/{filename}'


class Image(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    image = models.ImageField(upload_to=image_path, max_length=300, blank=True)
    thumbnail = models.ImageField(
        upload_to=image_thumb_path, max_length=300, blank=True)

    def save(self, *args, **kwargs) -> None:
        THUMBNAIL_SIZE = (400, 400)
        if self.image:
            image = PILImage.open(self.image)
            image = image.convert("RGB")
            image.thumbnail(THUMBNAIL_SIZE, PILImage.ANTIALIAS)
            temp_thumb = BytesIO()
            image.save(temp_thumb, "JPEG")
            temp_thumb.seek(0)
            self.thumbnail.save(
                self.image.name,
                ContentFile(temp_thumb.read()),
                save=False,
            )
            temp_thumb.close()
        elif self.thumbnail and not self.image:
            self.thumbnail.delete()
        return super().save(*args, **kwargs)


class Urls(models.Model):
    mal = models.URLField(blank=True, null=True)
    shiki = models.URLField(blank=True, null=True)
    manga_updates = models.URLField(blank=True, null=True)
    anilist = models.URLField(blank=True, null=True)
    world_art = models.URLField(blank=True, null=True)
    manga_dex = models.URLField(blank=True, null=True)
    manga_lib = models.URLField(blank=True, null=True)


class MetaTitle(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='%(class)s', null=True)
    premiere = models.DateField(null=True, blank=True)
    genre = models.ManyToManyField(
        Genre, related_name='%(class)s', blank=True)
    theme = models.ManyToManyField(
        Theme, related_name='%(class)s', blank=True)
    image = models.ForeignKey(
        Image, on_delete=models.SET_NULL, related_name='%(class)s', null=True, blank=True)
    description = models.TextField(blank=True)

    related_post = models.ManyToManyField(
        'post.Post', related_name='%(class)s', blank=True)
    urls = models.ForeignKey(Urls, on_delete=models.SET_NULL,
                             related_name='%(class)s', blank=True, null=True)
    score = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return str(self.title) if self.title else 'Name does not exist'

    def get_desc(self) -> str:
        if self.description:
            return self.description
        else:
            return "No description"


class Manga(MetaTitle):
    type = models.ForeignKey(MangaType, on_delete=models.SET_NULL,
                             related_name='manga', null=True, blank=True)
    authors = models.ForeignKey(
        Authors, on_delete=models.CASCADE, related_name='manga', null=True, blank=True)

    publisher = models.ManyToManyField(
        Publisher, related_name='manga', blank=True)
    volumes = models.IntegerField(null=True, blank=True)
    chapters = models.IntegerField(null=True, blank=True)
    demographic = models.ForeignKey(
        Demographic, on_delete=models.SET_NULL, related_name='manga', null=True, blank=True)
    magazine = models.ManyToManyField(
        Magazine, related_name='manga', blank=True)

    class Meta:
        ordering = ('title',)
        indexes = [
            models.Index(fields=['id', ]),
        ]

    def get_absolute_url(self) -> str:
        return reverse('manga_detail', kwargs={'pk': str(self.id)})

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        if self.title:
            self.title.delete()
        if self.authors:
            self.authors.delete()
        return super().delete(*args, **kwargs)


class Anime(MetaTitle):
    type = models.ForeignKey(AnimeType, on_delete=models.CASCADE,
                             related_name='anime', null=True, blank=True)
    studio = models.ManyToManyField(
        Studio, related_name='anime', blank=True)
    episodes = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('title',)
        indexes = [
            models.Index(fields=['id', ]),
        ]

    def get_absolute_url(self):
        return reverse('anime_detail', kwargs={'pk': str(self.id)})

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        if self.title:
            self.title.delete()
        return super().delete(*args, **kwargs)
