from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Genre, Studio, Anime,Manga, Demographic, AnimeType,MangaType, Publisher, Theme
from django.db.models import Count
from .filters import Filter,filter_by_name
import django.apps
# Create your views here.
class TitleList(ListView):
    template_name='list.html'
    context_object_name = 'list'

    def get_queryset(self):
        def filter(instance,name):
            list=self.request.GET.getlist(name)
            if list:
                for item in list:
                    instance=instance.filter(**filter_func(name=name,item=item))
            return instance
        url=self.request.build_absolute_uri().split('/')[3]
        if url=='manga':
            model=Manga.objects.select_related('title').values('id','title__original_name','image')
        elif url=='anime':
            model=Anime.objects.select_related('title').values('id','title__original_name','image')
        filter_func=Filter()
        list_filter=['genre','theme','demographic','type','publisher']
        for item in list_filter:
            model=filter(model,item)
        query = self.request.GET.get("q")
        if query:
            model= filter_by_name(query,model)
        model=model.annotate(relevance=Count('id')).order_by('-relevance','title__original_name') 
        return model

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url=self.request.build_absolute_uri().split('/')[3]
        if url=='manga':
            list_models=[MangaType,Demographic,Publisher,Theme,Genre]
        elif url=='anime':
           list_models=[AnimeType,Demographic,Publisher,Theme,Genre]
        filter_dict={}
        for item in list_models:
            filter_dict[f'{item._meta.model_name}'.capitalize()]=item.objects.all().values('name').order_by('name')
        query = self.request.GET.get("q")
        context.update({'filter':filter_dict,'model':'Manga','query': query})
        return context


class TitleDetail(DetailView):
    model= Manga
    template_name='manga/manga_detail.html'
    context_object_name = 'manga'