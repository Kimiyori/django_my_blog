from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Adaptation, Genre, Studio, Anime,Manga, Demographic, AnimeType,MangaType, Publisher, Theme
from django.db.models import Count
from .filters import Filter,filter_by_name,annotate_acc,values_acc
from urllib.parse import urlparse
from urllib.parse import parse_qs
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.expressions import Func
from django.db.models import F,ExpressionWrapper
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.aggregates import JSONBAgg
from django.db.models.fields import CharField,UUIDField,TextField
from django.db.models.functions import Cast
import uuid
from django.apps import apps
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
        url1 = self.request.build_absolute_uri()
        parsed_url = urlparse(url1)
        captured_value = parse_qs(parsed_url.query).keys()
        type=self.request.resolver_match.url_name
        if type=='manga_list':
            list_filter=['genre','theme','demographic','type','publisher','magazine','authors__artist','authors__author']
        elif type=='anime_list':
            list_filter=['genre','theme','type','studio']
        model=apps.get_model(app_label='titles',
                                  model_name=type.split('_')[0]).objects.all()
        filter_func=Filter()
        for item in list_filter:
            model=filter(model,item)
        query = self.request.GET.get("q")
        if query:
            model= filter_by_name(query,model)
        model=model.values('id','title__original_name','image').alias(relevance=Count('id')).order_by('-relevance','title__original_name') 
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
    template_name='titles/detail_test.html'
    context_object_name = 'item'
    def get_queryset(self):

        type=self.request.resolver_match.url_name
        id=self.kwargs['pk']
        tab=self.request.GET.get('tab')
        model=apps.get_model(app_label='titles',
                                  model_name=type.split('_')[0]).objects.filter(id=id).annotate(**annotate_acc(type,tab)).values(*values_acc(type,tab))  
        return model
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model=self.request.resolver_match.url_name.split('_')[0]
        tab=self.request.GET.get('tab')
        context.update({'model':model,'tab':tab,})
        return context
