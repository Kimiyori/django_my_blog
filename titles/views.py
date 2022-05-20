
from django.views.generic import ListView, DetailView
from .models import  Genre, Studio,  Demographic, AnimeType,MangaType, Publisher, Theme
from django.db.models import Count
from .filters import filter_by_name,annotate_acc,values_acc,filter_by_models

from django.apps import apps
# Create your views here.
class TitleList(ListView):
    template_name='titles/list.html'
    context_object_name = 'list'
    paginate_by = 10
    def get_queryset(self):
        type=self.request.resolver_match.url_name
        model=apps.get_model(app_label='titles',
                                  model_name=type.split('_')[0]).objects.all()
        model=filter_by_models(self.request,type,model)
        query = self.request.GET.get("q")
        if query:
            model= filter_by_name(query,model)
        model=model.values('id','title__original_name','image__thumbnail').alias(relevance=Count('id')).order_by('-relevance','title__original_name') 

        return model

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        type=self.request.resolver_match.url_name.split('_')[0]
        if type=='manga':
            list_models= {'Type':MangaType,'Demographic':Demographic,'Publisher':Publisher,'Theme':Theme,'Genre':Genre}
            model='Manga'
        elif type=='anime':
           list_models={'Type':AnimeType,'Demographic':Demographic,'Studio':Studio,'Theme':Theme,'Genre':Genre}
           model='Anime'
        filter_dict={}
        for key,item in list_models.items():
            filter_dict[key]=item.objects.all().values('name').order_by('name')
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
        if not tab:
            tab='info'
        model=apps.get_model(app_label='titles',
                                  model_name=type.split('_')[0]).objects.filter(id=id).annotate(**annotate_acc(type,tab)).values(*values_acc(type,tab))  
        return model
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model=self.request.resolver_match.url_name.split('_')[0]
        tab=self.request.GET.get('tab')
        context.update({'model':model,'tab':tab,})
        return context
