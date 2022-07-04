from django.contrib import admin
from .models import Post,Content,Text,Image,Video,File,Comment
from django.contrib.auth.models import Permission
from mptt.admin import MPTTModelAdmin



class MultiDBModelAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate database.
    using = 'dest_db'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = ('title', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', )
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'user_permissions':
            kwargs['queryset'] = Permission.objects.all(
            ).select_related('content_type')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

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
    using = 'test_db'
    list_display = ('post', )
    ordering=['post','order']

@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
     autocomplete_fields = ['post']


