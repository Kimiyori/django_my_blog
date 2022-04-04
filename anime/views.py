from django.shortcuts import render
from django.views.generic import ListView,DetailView
from anime.models import Genre, Studio,Anime,Demographic
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank,SearchHeadline
# Create your views here.

class SearchResultsList(ListView):
        model = Anime
        context_object_name = "list"
        template_name = "anime/search.html"

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            query = self.request.GET.get("q")
            context.update({'query': query})
            return context
        def get_queryset(self):
            query = self.request.GET.get("q") 
            search_vector = SearchVector('title__original_name','title__russian_name','title__english_name')
            search_query = SearchQuery(query)
            results= Anime.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by("-rank")
            return results
class AnimeList(ListView):
    model = Anime
    template_name='anime/list.html'
    context_object_name = 'list'

class AnimeDetail(DetailView):
    model= Anime
    template_name='anime/anime_detail.html'
    context_object_name = 'anime'
    

