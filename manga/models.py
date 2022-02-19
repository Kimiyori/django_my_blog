from django.db import models
import uuid
from django.urls import reverse

# Create your models here.


class Demographic(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='publishers/', blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name


class MangaType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    surname = models.CharField(max_length=200, null=True, blank=True)
    pseudonym = models.CharField(max_length=200, null=True, blank=True)
    photo = models.ImageField(upload_to='authors/', blank=True)

    def __str__(self):
        return f'{self.name}  {self.surname}'


class Theme(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=150, default='')

    def __str__(self):
        return self.name


class Magazine(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=150, default='')

    def __str__(self):
        return self.name


class Manga(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    title = models.CharField(max_length=500)

    type = models.ForeignKey(MangaType, on_delete=models.CASCADE,
                             related_name='manga', null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='manga', null=True, blank=True)
    publisher = models.ManyToManyField(
        Publisher, related_name='manga', blank=True)
    premiere = models.DateField(blank=True)
    volumes = models.IntegerField(null=True, blank=True)
    chapters = models.IntegerField(null=True, blank=True)
    genres = models.ManyToManyField(
        Genre, related_name='manga', blank=True)
    demographic = models.ForeignKey(
        Demographic, on_delete=models.CASCADE, related_name='manga', null=True, blank=True)
    themes = models.ManyToManyField(
        Theme, related_name='manga', blank=True)
    image = models.ImageField(upload_to='manga/', blank=True)
    magazine = models.ManyToManyField(
        Magazine, related_name='manga', blank=True)
    description = models.TextField( blank=True)
    class Meta:
        ordering = ('-title',)

    def __str__(self):
        return self.title
    def get_desc(self):
        if self.description:
            return self.description
        else:
            return "Нет описания"

class Title(models.Model):
    manga = models.OneToOneField(Manga, on_delete=models.CASCADE,
                                 related_name='item', null=True, blank=True)
    anime = models.OneToOneField('anime.Anime', on_delete=models.CASCADE,
                                 related_name='item', null=True, blank=True)
    original_name = models.CharField(max_length=300, null=True, blank=True)
    russian_name = models.CharField(max_length=300, null=True, blank=True)
    english_name = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.original_name
