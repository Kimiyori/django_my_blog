from django.contrib import admin
from .models import Anime,Studio,Type,Demographic,Genre
# Register your models here.
admin.site.register(Anime)
admin.site.register(Studio)
admin.site.register(Type)
admin.site.register(Demographic)
admin.site.register(Genre)