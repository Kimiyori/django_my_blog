from django.db import models
import uuid
from django.urls import reverse
"""from genre.models import Genre
from type.models import Type
from demographic.models import Demographic
from studio.models import Studio

from kind.models import Kind
# Create your models here.


class Item(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    type = models.ForeignKey(Type, on_delete=models.CASCADE,
                             related_name='anime_type', null=True, blank=True)
    title = models.CharField(max_length=500)
    alt_name = models.CharField(max_length=1000, blank=True)
    studio = models.ManyToManyField(
        Studio, related_name='anime_studio', blank=True)
    premiered = models.DateField(blank=True)
    episodes = models.IntegerField(blank=True)
    genres = models.ManyToManyField(
        Genre, related_name='anime_genres', blank=True)
    demographic = models.ForeignKey(
        Demographic, on_delete=models.CASCADE, related_name='anime_demo', null=True, blank=True)
    image = models.ImageField(upload_to='item_pic/', blank=True)
    kind= models.ForeignKey(
        Kind, on_delete=models.CASCADE, related_name='kind', null=True, blank=True)
    class Meta:
        ordering = ('-title',)

    def __str__(self):
        return self.title
"""