from django.contrib import admin
from .models import Demographic,Author,Genre,MangaType,Publisher,Manga,Theme,Title,Magazine
# Register your models here.
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

"""class AlterInline(admin.TabularInline):
 model = AlterName

@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
 inlines = [AlterInline]
"""