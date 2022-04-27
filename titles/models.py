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


class AuthorTable(models.Model):
    name=models.CharField(max_length=200, null=True, blank=True)
    pseudonym = models.CharField(max_length=200, null=True, blank=True)
    photo = models.ImageField(upload_to='authors/', blank=True)

    def __str__(self):
        return f'{self.name}'

class Authors(models.Model):
    author= models.ForeignKey(AuthorTable, on_delete=models.CASCADE,related_name='authors_author', null=True, blank=True)
    artist= models.ForeignKey(AuthorTable, on_delete=models.CASCADE,related_name='authors_artist', null=True, blank=True)

    def __str__(self):
        return f'Author-{self.author} Artist-{self.artist}'
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
            return "Doesn't have name"




class Adaptation(models.Model):
    adaptation= models.ForeignKey('Anime', on_delete=models.CASCADE,
                               related_name='based_on', null=True, blank=True)
    based_on= models.ForeignKey('Manga', on_delete=models.CASCADE,
                               related_name='adaptation', null=True, blank=True)




class SequelPrequelAnime(models.Model):
    sequel= models.ForeignKey('Anime', on_delete=models.CASCADE,
                               related_name='prequel', null=True, blank=True)
    prequel= models.ForeignKey('Anime', on_delete=models.CASCADE,
                               related_name='sequel', null=True, blank=True)

class SequelPrequelManga(models.Model):
    sequel= models.ForeignKey('Manga', on_delete=models.CASCADE,
                               related_name='prequel', null=True, blank=True)
    prequel= models.ForeignKey('Manga', on_delete=models.CASCADE,
                               related_name='sequel', null=True, blank=True)
def image_path_manga(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'manga/{0}/{1}'.format(instance.id, filename)
class Manga(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                             related_name='manga')

    type = models.ForeignKey(MangaType, on_delete=models.CASCADE,
                             related_name='manga', null=True, blank=True)
    authors = models.ForeignKey(Authors, on_delete=models.CASCADE,related_name='manga', null=True, blank=True)

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
    image = models.ImageField(upload_to=image_path_manga, blank=True)
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




class AnimeType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name

class Studio(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='studios/', blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name

def image_path_anime(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'anime/{0}/{1}'.format(instance.id, filename)

class Anime(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                             related_name='anime')
    type = models.ForeignKey(AnimeType, on_delete=models.CASCADE,
                             related_name='anime', null=True, blank=True)
    studio = models.ManyToManyField(
        Studio, related_name='anime', blank=True)
    premiere = models.DateField(null=True, blank=True)
    episodes = models.IntegerField(null=True, blank=True)
    genre = models.ManyToManyField(
        Genre, related_name='anime', blank=True)
    theme = models.ManyToManyField(
        Theme, related_name='anime', blank=True)
    image = models.ImageField(upload_to=image_path_anime, blank=True)
    description = models.TextField(null=True,  blank=True)


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
        return reverse('anime_detail', kwargs={'pk':str(self.id)})
