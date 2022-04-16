from django.shortcuts import render
from django.views.generic import ListView,DetailView
from django.shortcuts import get_object_or_404
from .models import Demographic,Author,Genre,MangaType,Publisher,Manga, Theme
from django.db.models import Q 
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank,SearchHeadline
from django.db.models import Count
from django.urls import reverse
from django.db.models import F
from django.db.models import Count
from.filter import Filter
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
    template_name='manga/list.html'
    context_object_name = 'list'

    def get_queryset(self):

        def filter(instance,name):
            list=self.request.GET.getlist(name)
            filter_func=Filter()
            if list:
                for item in list:
                    instance=instance.filter(**filter_func(name=name,item=item))
            return instance

        manga=Manga.objects.all().values('id','title__original_name','image')
        list_filter=['genre','theme','demographic','type','publisher']
        for item in list_filter:
            manga=filter(manga,item)
        return manga.annotate(relevance=Count('id')).order_by('-relevance','title__original_name') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genres=Genre.objects.all().values('name').order_by('name')
        themes=Theme.objects.all().values('name').order_by('name')
        demographic=Demographic.objects.all().values('name').order_by('name')
        type=MangaType.objects.all().values('name').order_by('name')
        publisher=Publisher.objects.all().values('name').order_by('name')
        context.update({'filter':{'Demographic':demographic,'Type':type,'Publisher':publisher,'Theme':themes,'Genre': genres}})
        return context

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