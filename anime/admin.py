from django.contrib import admin
from .models import Anime, Studio, AnimeType
from manga.admin import TitleInline
from manga.models import Genre, Title, Manga
from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError
from django.urls import path
from django.template.response import TemplateResponse
@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    inlines = [TitleInline]
    change_form_template = 'admin/anime/change_form.html'

    def get_title_obj(self, obj):
        return Title.objects.filter(manga=obj.source).first()

    def save_model(self, request, obj, form, change):
        exist_anime = Anime.objects.filter(id=obj.id).first()
        if obj.source:
            source = obj.source
            obj.author = source.author
            obj.description = source.description
            cur_title = self.get_title_obj(obj)
            if exist_anime and exist_anime.source != obj.source:
                if cur_title and cur_title.anime != None:
                    raise DataError
                if exist_anime.source != None:
                    prev_title = self.get_title_obj(exist_anime)
                    if prev_title:
                        prev_title.anime = None
                        prev_title.save()
                if cur_title:
                    cur_title.anime = obj
                    cur_title.save()
            else:
                if cur_title:
                    cur_title.anime = obj
                    obj.save()
                    cur_title.save()
                else:
                    raise DataError
        elif not obj.source and exist_anime:
            obj.author = None
            obj.description = None
            prev_title = self.get_title_obj(exist_anime)
            prev_title.anime = None
            prev_title.save()
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super(AnimeAdmin, self).save_related(request, form, formsets, change)
        if form.instance.source:
            form.instance.genres.set(form.instance.source.genres.all())
            form.instance.themes.set(form.instance.source.themes.all())
        else:
            form.instance.genres.set([])
            form.instance.themes.set([])


@admin.register(AnimeType)
class AnimeTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
