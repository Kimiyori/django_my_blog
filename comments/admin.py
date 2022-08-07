from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import *
# Register your models here.
@admin.register(CommentPost)
class CommentPostAdmin(MPTTModelAdmin):
     autocomplete_fields = ['model']

@admin.register(CommentAnime)
class CommentAnimeAdmin(MPTTModelAdmin):
     autocomplete_fields = ['model']

@admin.register(CommentManga)
class CommentMangaAdmin(MPTTModelAdmin):
     autocomplete_fields = ['model']