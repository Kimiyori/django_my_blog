from django.db import models

# Create your models here.

class Type(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    slug = models.SlugField(max_length=250,default='')
    class Meta:
        ordering = ('-name',)
    def __str__(self):
        return self.name