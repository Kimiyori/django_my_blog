from django.db import models

# Create your models here.
class Kind(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=250,default='')    
    def __str__(self):
        return self.name