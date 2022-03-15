from django.contrib import admin
from .models import Post,Related,Content,Text,Image,Video,File

@admin.register(Related)
class RelatedAdmin(admin.ModelAdmin):
    autocomplete_fields = ['anime','manga']
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'related_to', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass
@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    pass
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    pass
@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('post', )
    ordering=['post','order']

