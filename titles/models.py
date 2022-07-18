from django.db import models
import uuid
from django.urls import reverse
from django_cleanup import cleanup

# Create your models here.

class Demographic(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self)-> str:
        return str(self.name)


class Genre(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('name',)

    def __str__(self)->str:
        return str(self.name)


class Publisher(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='publishers/', blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self)->str:
        return str(self.name)


class MangaType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self)->str:
        return str(self.name)


class AuthorTable(models.Model):
    name=models.CharField(max_length=200, null=True, blank=True)
    pseudonym = models.CharField(max_length=200, null=True, blank=True)
    photo = models.ImageField(upload_to='authors/', blank=True)

    def __str__(self)->str:
        return str(self.name)

class Authors(models.Model):
    author= models.ForeignKey(AuthorTable, on_delete=models.CASCADE,related_name='authors_author', null=True, blank=True)
    artist= models.ForeignKey(AuthorTable, on_delete=models.CASCADE,related_name='authors_artist', null=True, blank=True)

    def __str__(self)->str:
        return f'Author-{self.author} Artist-{self.artist}'
class Theme(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=150, default='')

    def __str__(self)->str:
        return str(self.name)


class Magazine(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='magazines/', blank=True)
    slug = models.SlugField(max_length=150, default='')

    def __str__(self)->str:
        return str(self.name)



class Title(models.Model):


    original_name = models.CharField(max_length=300, null=True, blank=True)
    russian_name = models.CharField(max_length=300, null=True, blank=True)
    english_name = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self)->str:
        if self.original_name:
            return str(self.original_name)
        elif self.english_name:
            return str(self.english_name)
        elif self.russian_name:
            return str(self.russian_name)
        else:
            return "Doesn't have name"



class AnimeType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self)->str:
        return str(self.name)

class Studio(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='studios/', blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self)->str:
        return str(self.name)


class Adaptation(models.Model):
    adaptation= models.ForeignKey('Anime', on_delete=models.CASCADE,
                               related_name='based_on', null=True, blank=True)
    based_on= models.ForeignKey('Manga', on_delete=models.CASCADE,
                               related_name='adaptation', null=True, blank=True)

class AdaptationReverse(models.Model):
    adaptation= models.ForeignKey('Manga', on_delete=models.CASCADE,
                               related_name='based_on', null=True, blank=True)
    based_on= models.ForeignKey('Anime', on_delete=models.CASCADE,
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
    image = models.ImageField(upload_to=image_path, max_length=300,blank=True)
    thumbnail=models.ImageField(upload_to=image_thumb_path,max_length=300, blank=True)

class Urls(models.Model):
    mal=models.URLField()

class MetaTitle(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                             related_name='%(class)s',null=True)
    premiere = models.DateField(null=True,blank=True)
    genre = models.ManyToManyField(
        Genre, related_name='%(class)s', blank=True)
    theme = models.ManyToManyField(
        Theme, related_name='%(class)s', blank=True)
    image = models.ForeignKey(
        Image, on_delete=models.SET_NULL, related_name='%(class)s', null=True, blank=True)
    description = models.TextField( blank=True)

    related_post=models.ManyToManyField(
        'post.Post', related_name='%(class)s', blank=True)
    urls=models.ForeignKey(Urls, on_delete=models.SET_NULL,
                             related_name='%(class)s',blank=True,null=True)
    score=models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    class Meta:
        abstract=True

    def __str__(self)-> str:
        name='Not name' 
        if self.title:
            if getattr(self.title,'original_name'):
                name= str(self.title.original_name)
            elif getattr(self.title,'english_name'):
                name=  str(self.title.english_name)
            elif getattr(self.title,'russian_name'):
                name= str(self.title.russian_name)
        return name
            
    def get_desc(self)->str:
        if self.description:
            return self.description
        else:
            return "Нет описания"


class Manga(MetaTitle):
    type = models.ForeignKey(MangaType, on_delete=models.SET_NULL,
                             related_name='manga', null=True, blank=True)
    authors = models.ForeignKey(Authors, on_delete=models.CASCADE,related_name='manga', null=True, blank=True)

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
            models.Index(fields=['id',]),
        ]


    def get_absolute_url(self)->str:
        return reverse('manga_detail', kwargs={'pk':str(self.id)})

    def delete(self,*args,**kwargs):
        if self.image:
            self.image.delete()
        if self.title:
            self.title.delete()
        if self.authors:
            self.authors.delete()
        return super().delete(*args,**kwargs)




class Anime(MetaTitle):
    type = models.ForeignKey(AnimeType, on_delete=models.CASCADE,
                             related_name='anime', null=True, blank=True)
    studio = models.ManyToManyField(
        Studio, related_name='anime', blank=True)
    episodes = models.IntegerField(null=True, blank=True)



    class Meta:
        ordering = ('title',)
        indexes = [
            models.Index(fields=['id',]),
        ]
        

    def get_absolute_url(self):
        return reverse('anime_detail', kwargs={'pk':str(self.id)})
        
    def delete(self,*args,**kwargs):
        if self.image:
            self.image.delete()
        if self.title:
            self.title.delete()
        return super().delete(*args,**kwargs)