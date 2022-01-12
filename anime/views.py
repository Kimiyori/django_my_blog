from django.shortcuts import render
"""from django.views.generic import ListView,DetailView
from anime.models import Genre, Studio,Anime,Demographic
# Create your views here.
class StudiosList(ListView):
    model = Studio
    template_name='anime/studios/list.html'
    context_object_name = 'list_studios'

class AnimeList(ListView):
    model = Anime
    paginate_by=1 
    template_name='anime/anime_list.html'
    context_object_name = 'anime_list'

class AnimeDetail(DetailView):
    model= Anime
    template_name='anime/anime_detail.html'
    context_object_name = 'anime'
    

class GenreAnimeList(DetailView):
    model=Genre
    template_name='anime/genres/genre_detail.html'
    context_object_name = 'genre'

class DemoAnimeList(DetailView):
    model=Demographic
    template_name='anime/demographic/demographic_detail.html'
    context_object_name = 'demo'

class StudiosDetailList(DetailView):
    model=Studio
    template_name='anime/studios/detail.html'
    context_object_name = 'studio'
"""

