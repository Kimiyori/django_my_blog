from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Demographic,Author,Genre,MangaType,Publisher,Manga,Theme,Title,Magazine,Anime, Studio, AnimeType
# Register your models here.

@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    autocomplete_fields=['title','source','type','author',]
    search_fields=['title']
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

@admin.register(Demographic)
class DemoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
@admin.register(Genre)
class DemoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'pseudonym': ('name','surname')}
    search_fields = ['name','surname']
@admin.register(MangaType)
class MangaTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    search_fields = ['original_name','english_name','russian_name']
    pass

@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
    search_fields = ['title']
    autocomplete_fields=['title','type','author','demographic']
    

@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}