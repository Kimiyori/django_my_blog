
from django.db import models
import uuid 
from django.contrib.auth import get_user_model
from django.utils import timezone
from titles.models import Manga,Anime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey,  GenericRelation
from .fields import OrderField
from django.template.loader import render_to_string
from django.apps import apps
from django_cleanup import cleanup


# Create your models here.
User=get_user_model()



class Related(models.Model):
    manga = models.OneToOneField(Manga, related_name='related',null=True, blank=True,
                                 on_delete=models.CASCADE)
    anime = models.OneToOneField(Anime,related_name='related', null=True, blank=True,
                                 on_delete=models.CASCADE)
    
    def __str__(self):
        if self.manga:
            return self.manga.title.original_name
        elif self.anime:
            return self.anime.title.original_name
        else:
             return 'Not related'

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,self).get_queryset().filter(status='published')

def main_path(instance, filename):
    return 'post/{0}/{1}/{2}/{3}'.format(instance.author.id,instance.id,'image', filename)
class Post(models.Model):
    STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('published', 'Published'),
    )
    title = models.CharField(max_length=500)
    main_image = models.ImageField(upload_to=main_path)
    related_to=models.ForeignKey(Related, related_name='post', on_delete=models.CASCADE,blank=True,null=True)
    id = models.UUIDField(
                            primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post')
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    objects = models.Manager() # The default manager.
    published = PublishedManager() # Our custom manager.
    class Meta:
        ordering = ('-publish',)
    def __str__(self):
        return self.title


class Content(models.Model):
    post = models.ForeignKey(Post,related_name='contents',on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE,limit_choices_to={'model__in':(
                                                                                                        'text',
                                                                                                        'video',
                                                                                                        'image',
                                                                                                        'file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    order = OrderField(blank=True, for_fields=['post'])
    class Meta:
        ordering = ['order']

    
    

def path(instance, filename):
    return 'post/{0}/{1}/{2}/{3}'.format(instance.post.author.id,instance.post.id,instance._meta.model_name, filename)
@cleanup.ignore
class ItemBase(models.Model):
    post = models.ForeignKey(Post,
    related_name='%(class)s_related',
    on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
    def __str__(self):
        return f'{self.__class__.__name__} from {self.post}'
    
    def get_model_name(self):
        return self._meta.model_name
    def render(self):
        return render_to_string(
        f'post/content/{self._meta.model_name}.html',
        {'item': self})
class Text(ItemBase):
    text = models.TextField()
    relation = GenericRelation(Content ,content_type_field='content_type',
    object_id_field='object_id', related_query_name='text')
    
class File(ItemBase):
    file = models.FileField(upload_to=path)
    relation = GenericRelation(Content ,content_type_field='content_type',
    object_id_field='object_id', related_query_name='file')
class Image(ItemBase):
    image = models.ImageField(upload_to=path)
    relation = GenericRelation(Content ,content_type_field='content_type',
    object_id_field='object_id', related_query_name='image')
class Video(ItemBase):
    video = models.URLField()
    relation = GenericRelation(Content ,content_type_field='content_type',
    object_id_field='object_id', related_query_name='video')