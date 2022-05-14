from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Demographic,Genre,MangaType,Publisher,Manga,Theme,Title,Magazine,Anime, Studio, AnimeType,Adaptation,SequelPrequelAnime,SequelPrequelManga,Authors,AuthorTable,Image
# Register your models here.

class AdaptationInline(admin.TabularInline):
    model = Adaptation
    autocomplete_fields=['adaptation','based_on']
    extra=1
class PrequelAnimeInline(admin.TabularInline):
    model = SequelPrequelAnime
    autocomplete_fields=['prequel']
    fk_name='sequel'
    extra=1
class SequelAnimeInline(admin.TabularInline):
    model = SequelPrequelAnime
    autocomplete_fields=['sequel']
    fk_name='prequel'
    extra=1
class PrequelMangaInline(admin.TabularInline):
    model = SequelPrequelManga
    autocomplete_fields=['prequel']
    fk_name='sequel'
    extra=1
class SequelMangaInline(admin.TabularInline):
    model = SequelPrequelManga
    autocomplete_fields=['sequel']
    fk_name='prequel'
    extra=1
@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    inlines = [
       AdaptationInline,
       PrequelAnimeInline,SequelAnimeInline
    ]
    filter_horizontal=['genre','studio','theme',]
    autocomplete_fields=['title','type',]
    search_fields=['title']
    change_form_template = 'admin/anime/change_form.html'



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
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass
@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
@admin.register(AuthorTable)
class AuthorTableAdmin(admin.ModelAdmin):
    prepopulated_fields = {'pseudonym': ('name',)}
    search_fields = ['name']
@admin.register(Authors)
class AuthorsAdmin(admin.ModelAdmin):
    autocomplete_fields=['author','artist',]
    search_fields = ['author','artist',]
@admin.register(MangaType)
class MangaTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    search_fields = ['original_name','english_name','russian_name']


@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
    inlines = [
       AdaptationInline,
       SequelMangaInline,PrequelMangaInline
    ]
    filter_horizontal=['genre','publisher','magazine','theme',]
    search_fields = ['title']
    autocomplete_fields=['title','type','authors','demographic']
    

@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}