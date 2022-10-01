from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from post.models import Post
from django.contrib.auth import get_user_model

from titles.models import Anime, Manga
# Create your models here.
User = get_user_model()


class CommentMeta(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='%(class)s_children')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='%(class)s_comments')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    class MPTTMeta:
        order_insertion_by = ['created']

    def __str__(self) -> str:
        return f'Comment by {self.author}'
    
    @classmethod
    def get_comments_for_post(cls,pk):
        return cls.objects.select_related(
            'author__profile').filter(model=pk)


class CommentPost(CommentMeta):
    model = models.ForeignKey(Post,
                             related_name='comments',
                             on_delete=models.CASCADE)


class CommentManga(CommentMeta):
    model = models.ForeignKey(Manga,
                              related_name='comments',
                              on_delete=models.CASCADE)
class CommentAnime(CommentMeta):
    model = models.ForeignKey(Anime,
                              related_name='comments',
                              on_delete=models.CASCADE)