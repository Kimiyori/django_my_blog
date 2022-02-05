from django.contrib import admin
from .models import Demographic,Author,Genre,MangaType,Publisher,Manga
# Register your models here.
@admin.register(Demographic)
class DemoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'pseudonym': ('name','surname')}

@admin.register(MangaType)
class MangaTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
    pass


"""class AlterInline(admin.TabularInline):
 model = AlterName

@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
 inlines = [AlterInline]
"""