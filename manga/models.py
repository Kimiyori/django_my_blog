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


class Manga(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    title = models.CharField(max_length=500)

    type = models.ForeignKey(MangaType, on_delete=models.CASCADE,
                             related_name='anime_type', null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='manga', null=True, blank=True)
    publisher = models.ManyToManyField(
        Publisher, related_name='manga', blank=True)
    premiere = models.DateField(blank=True)
    volumes = models.IntegerField(blank=True)
    chapters = models.IntegerField(blank=True)
    genres = models.ManyToManyField(
        Genre, related_name='manga', blank=True)
    demographic = models.ForeignKey(
        Demographic, on_delete=models.CASCADE, related_name='manga', null=True, blank=True)
    image = models.ImageField(upload_to='manga/', blank=True)

    class Meta:
        ordering = ('-title',)

    def __str__(self):
        return self.title
