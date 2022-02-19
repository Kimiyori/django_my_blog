from django.shortcuts import render
from django.views.generic import ListView,DetailView
from anime.models import Genre, Studio,Anime,Demographic
# Create your views here.


class AnimeList(ListView):
    model = Anime
    template_name='anime/list.html'
    context_object_name = 'list'

class AnimeDetail(DetailView):
    model= Anime
    template_name='anime/anime_detail.html'
    context_object_name = 'anime'
    

