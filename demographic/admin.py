from django.contrib import admin
from .models import Demographic
# Register your models here.
@admin.register(Demographic)
class DemoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}