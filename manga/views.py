from django.shortcuts import render
from django.views.generic import ListView,DetailView
from django.shortcuts import get_object_or_404
from .models import Demographic,Author,Genre,MangaType,Publisher,Manga
from django.db.models import Q 
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank,SearchHeadline
# Create your views here.
class SearchResultsList(ListView):
        model = Manga
        context_object_name = "list"
        template_name = "manga/search.html"

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            query = self.request.GET.get("q")
            context.update({'query': query})
            return context
        def get_queryset(self):
            query = self.request.GET.get("q") 
            search_vector = SearchVector('title__original_name','title__russian_name','title__english_name')
            search_query = SearchQuery(query)
            results= Manga.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by("-rank")
            return results
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