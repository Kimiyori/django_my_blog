from django.db import models
import uuid 
from django.contrib.auth import get_user_model

# Create your models here.

class Studio(models.Model):
    studio = models.CharField(max_length=100,null=True,blank=True)
    image=models.ImageField(upload_to='studio_pic/',blank=True)
    class Meta:
        ordering = ('-studio',)
    def __str__(self):
        return self.studio


class Type(models.Model):
    type = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        ordering = ('-type',)
    def __str__(self):
        return self.type

class Demographic(models.Model):
    demographic=models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        ordering = ('-demographic',)
    def __str__(self):
        return self.demographic

class Genre(models.Model):
    genres=models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        ordering = ('-genres',)
    def __str__(self):
        return self.genres

class Anime(models.Model):
    id = models.UUIDField(
                            primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    type = models.ForeignKey(Type,on_delete=models.CASCADE,related_name='anime_type',null=True,blank=True)
    title = models.CharField(max_length=500)
    alt_name=models.CharField(max_length=1000,blank=True)
    studio = models.ManyToManyField(Studio,related_name='anime_studio',blank=True)
    premiered = models.DateField(blank=True)
    episodes=models.IntegerField(blank=True)
    genres = models.ManyToManyField(Genre,related_name='anime_genres',blank=True)
    demographic = models.ForeignKey(Demographic,on_delete=models.CASCADE,related_name='anime_demo',null=True,blank=True)
    image=models.ImageField(upload_to='anime_pic/',blank=True)
    class Meta:
        ordering = ('-title',)
    def __str__(self):
        return self.title