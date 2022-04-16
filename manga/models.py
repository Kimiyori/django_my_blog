from django.db import models
import uuid
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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

class Title(models.Model):

    original_name = models.CharField(max_length=300, null=True, blank=True)
    russian_name = models.CharField(max_length=300, null=True, blank=True)
    english_name = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        if self.original_name:
            return str(self.original_name)
        elif self.english_name:
            return str(self.english_name)
        elif self.russian_name:
            return str(self.russian_name)
        else:
            return 'Not name'

def image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'anime/{0}/{1}'.format(instance.title.original_name, filename)
class Manga(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                             related_name='manga')

    type = models.ForeignKey(MangaType, on_delete=models.CASCADE,
                             related_name='manga', null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='manga', null=True, blank=True)
    publisher = models.ManyToManyField(
        Publisher, related_name='manga', blank=True)
    premiere = models.DateField(blank=True)
    volumes = models.IntegerField(null=True, blank=True)
    chapters = models.IntegerField(null=True, blank=True)
    genre = models.ManyToManyField(
        Genre, related_name='manga', blank=True)
    demographic = models.ForeignKey(
        Demographic, on_delete=models.CASCADE, related_name='manga', null=True, blank=True)
    theme = models.ManyToManyField(
        Theme, related_name='manga', blank=True)
    image = models.ImageField(upload_to=image_path, blank=True)
    magazine = models.ManyToManyField(
        Magazine, related_name='manga', blank=True)
    description = models.TextField( blank=True)
    class Meta:
        ordering = ('-title',)

    def __str__(self):
        if self.title.original_name:
            return str(self.title.original_name)
        elif self.title.english_name:
            return str(self.title.english_name)
        elif self.title.russian_name:
            return str(self.title.russian_name)
        else:
            return 'Not name'
    def get_desc(self):
        if self.description:
            return self.description
        else:
            return "Нет описания"
    def get_absolute_url(self):
        return reverse('manga_detail', kwargs={'pk':str(self.id)})

