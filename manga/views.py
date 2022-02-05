from django.shortcuts import render
from django.views.generic import ListView,DetailView
from django.shortcuts import get_object_or_404
from .models import Demographic,Author,Genre,MangaType,Publisher,Manga
from django.db.models import Q 
# Create your views here.
class MangaList(ListView):
    model = Manga
    template_name='manga/list.html'
    context_object_name = 'list'
    #def get_queryset(self):
        #query=self.
        #return self.model.objects.filter(Q(manga__title__icontains='Tetsug'))

class GenreList(DetailView):
    model=Genre
    template_name='manga/genre/list.html'
    context_object_name = 'list'
    #def get_queryset(self):
    #return self.model.objects.filter(Q(manga__title__icontains='Tetsug'))
class MangaDetail(DetailView):
    model= Manga
    template_name='manga/manga_detail.html'
    context_object_name = 'manga'