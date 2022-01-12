from django.contrib import admin
from .models import Kind
# Register your models here.
@admin.register(Kind)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}