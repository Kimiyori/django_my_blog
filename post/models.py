from django.db import models
import uuid 
from django.contrib.auth import get_user_model
from django.utils import timezone
from manga.models import Manga
# Create your models here.
"""User=get_user_model()
class Post(models.Model):
    STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('published', 'Published'),
    )
    title = models.CharField(max_length=500)
    id = models.UUIDField(
                            primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    author = models.ForeignKey(User,
    on_delete=models.CASCADE,
    related_name='blog_posts')
    body = models.TextField()
    anime=models.ForeignKey(Manga,on_delete=models.CASCADE,
    related_name='post')
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,
    choices=STATUS_CHOICES, 
    default='draft')
    class Meta:
        ordering = ('-publish',)
    def __str__(self):
        return self.title"""