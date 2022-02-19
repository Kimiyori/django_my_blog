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
    pass
class TitleInline(admin.StackedInline):
    model = Title
    fields=['original_name','english_name','russian_name']
@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
    inlines = [TitleInline]
    autocomplete_fields=['type','author','demographic']
    

@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

"""class AlterInline(admin.TabularInline):
 model = AlterName

@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
 inlines = [AlterInline]
"""