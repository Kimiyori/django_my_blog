from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Genre, Studio, Anime,Manga, Demographic, AnimeType,MangaType, Publisher, Theme
from django.db.models import Count
from .filters import Filter,filter_by_name
from urllib.parse import urlparse
from urllib.parse import parse_qs

# Create your views here.
class TitleList(ListView):
    template_name='titles/list.html'
    context_object_name = 'list'

    def get_queryset(self):
        def filter(instance,name):
            temp=name.split('__')[-1]
            if temp in captured_value:
                list=self.request.GET.getlist(temp)
                if list:
                    for item in list:
                        instance=instance.filter(**filter_func(name=name,item=item))
            return instance
        url=self.request.build_absolute_uri().split('/')[3]
        url1 = self.request.build_absolute_uri()
        parsed_url = urlparse(url1)
        captured_value = parse_qs(parsed_url.query).keys()
        if url=='manga':
            model=Manga.objects.select_related('title')
            list_filter=['genre','theme','demographic','type','publisher','magazine','authors__artist','authors__author']
        elif url=='anime':
            model=Anime.objects.select_related('title')
            list_filter=['genre','theme','type','studio']
        filter_func=Filter()
        for item in list_filter:
            model=filter(model,item)
        query = self.request.GET.get("q")
        if query:
            model= filter_by_name(query,model)
        model=model.values('id','title__original_name','image').annotate(relevance=Count('id')).order_by('-relevance','title__original_name') 
        return model

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url=self.request.build_absolute_uri().split('/')[3]
        if url=='manga':
            list_models=[MangaType,Demographic,Publisher,Theme,Genre]
            model='Manga'
        elif url=='anime':
           list_models=[AnimeType,Demographic,Studio,Theme,Genre]
           model='Anime'
        filter_dict={}
        for item in list_models:
            filter_dict[f'{item._meta.model_name}'.capitalize()]=item.objects.all().values('name').order_by('name')
        query = self.request.GET.get("q")
        context.update({'filter':filter_dict,'model':model,'query': query})
        return context


class TitleDetail(DetailView):
    template_name='titles/detail.html'
    context_object_name = 'item'
    def get_queryset(self):
        url=self.request.build_absolute_uri().split('/')[3]
        id=self.request.build_absolute_uri().split('/')[4]
        if url=='manga':
            model=Manga.objects.prefetch_related('genre','theme','magazine','publisher').select_related('title','demographic','type','authors').filter(id=id)
        elif url=='anime':
            model=Anime.objects.prefetch_related('genre','theme','studio').select_related('title','source','type','authors').filter(id=id)
        return model
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url=self.request.build_absolute_uri().split('/')[3]
        if url=='manga':
            model='Manga'
        elif url=='anime':
           model='Anime'
        context.update({'model':model})
        return context
