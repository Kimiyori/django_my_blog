from django.db import models
import uuid 
from django.contrib.auth import get_user_model

# Create your models here.

class Studio(models.Model):
    studio = models.CharField(max_length=100)
    image=models.ImageField(upload_to='studio_pic/',blank=True)
    class Meta:
        ordering = ('-studio',)
    def __str__(self):
        return self.studio


class Type(models.Model):
    type = models.CharField(max_length=100)
    class Meta:
        ordering = ('-type',)
    def __str__(self):
        return self.type

class Anime(models.Model):
    id = models.UUIDField(
                            primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    type = models.ForeignKey(Type,on_delete=models.CASCADE,related_name='anime_type')
    title = models.CharField(max_length=500)
    alt_name=models.CharField(max_length=1000)
    studio = models.ForeignKey(Studio,on_delete=models.CASCADE,related_name='anime_studio')
    premiered = models.DateTimeField()
    episodes=models.DecimalField(decimal_places=0,max_digits=5)
    genres=models.CharField(max_length=100)
    demographic=models.CharField(max_length=100)
    image=models.ImageField(upload_to='anime_pic/',blank=True)
    class Meta:
        ordering = ('-title',)
    def __str__(self):
        return self.title