from django.contrib import admin
from .models import Studio
# Register your models here.
@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}