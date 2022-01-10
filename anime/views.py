from django.shortcuts import render
from django.views.generic import ListView,DetailView
from anime.models import Studio,Anime
# Create your views here.
class StudiosList(ListView):
    model = Studio
    template_name='anime/studios/list.html'
    context_object_name = 'list_studios'

class AnimeList(ListView):
    model = Anime
    template_name='anime/anime_list.html'
    context_object_name = 'anime_list'

class AnimeDetail(DetailView):
    model= Anime
    template_name='anime/anime_detail.html'
    context_object_name = 'anime'