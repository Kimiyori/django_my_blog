from django.contrib import admin
from .models import Genre
# Register your models here.
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}