from django.contrib import admin
from .models import Anime, Studio, AnimeType
from manga.models import Genre, Title, Manga
from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib.contenttypes.admin import  GenericStackedInline

@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    autocomplete_fields=['title','source','type','author',]

    change_form_template = 'admin/anime/change_form.html'

    """def get_title_obj(self, obj):
        return Title.objects.filter(manga=obj.source).first()

    def save_model(self, request, obj, form, change): 
        prev_anime = Anime.objects.filter(id=obj.id).first()
        if obj.source:
            cur_title = self.get_title_obj(obj)
            if prev_anime and prev_anime.source != obj.source:
                if prev_anime.source != None:
                    prev_title = self.get_title_obj(prev_anime)
                    if prev_title:
                        prev_title.anime = None
                        prev_title.save()
                if cur_title:
                    if cur_title.anime != None:
                        cur_title.anime = None
                        cur_title.save()
                    cur_title.anime = obj
                    cur_title.save()
            else:
                if cur_title:
                    if cur_title.anime != None:
                        cur_title.anime = None
                        cur_title.save()
                    obj.save()
                    cur_title.anime = obj
                    cur_title.save()
        elif not obj.source:
            prev_title = self.get_title_obj(prev_anime)
            if prev_title:
                prev_title.anime = None
                prev_title.save()
        super().save_model(request, obj, form, change)"""



@admin.register(AnimeType)
class AnimeTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
