from django.db import models
import uuid
from django.urls import reverse
from manga.models import Demographic,Author,Genre,Publisher,Manga,Theme,Title,Magazine

class AnimeType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name

class Studio(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='manga/', blank=True)
    slug = models.SlugField(max_length=250, default='')

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name

def image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'anime/{0}/{1}'.format(instance.item.original_name, filename)
class Anime(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    source=models.ForeignKey(Manga, on_delete=models.CASCADE,
                               related_name='anime', null=True, blank=True)
    type = models.ForeignKey(AnimeType, on_delete=models.CASCADE,
                             related_name='anime', null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='anime', null=True, blank=True)
    studio = models.ManyToManyField(
        Studio, related_name='anime', null=True, blank=True)
    premiere = models.DateField(null=True, blank=True)
    episodes = models.IntegerField(null=True, blank=True)
    genres = models.ManyToManyField(
        Genre, related_name='anime', null=True, blank=True)
    themes = models.ManyToManyField(
        Theme, related_name='anime', null=True, blank=True)
    image = models.ImageField(upload_to=image_path, blank=True)
    description = models.TextField(null=True,  blank=True)



    def __str__(self):
        try:
            return str(self.item.original_name)
        except Exception:
            return str(self.id) 
            
    def get_desc(self):
        if self.description:
            return self.description
        else:
            return "Нет описания"