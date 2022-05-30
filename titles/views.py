
from django.views.generic import ListView, DetailView
from .models import Genre, Studio,  Demographic, AnimeType, MangaType, Publisher, Theme
from django.db.models import Count
from .filters import filter_by_name, annotate_acc, values_acc, filter_by_models
from django.core.cache import cache
from django.apps import apps
from django.core.cache.utils import make_template_fragment_key
from django.views.generic.base import TemplateResponseMixin, View
from .paginator import LargeTablePaginator
from . import tasks
# Create your views here.


class TitleList(ListView):
    template_name = 'titles/list.html'
    context_object_name = 'list'
    paginate_by = 20
    paginator=LargeTablePaginator

    def get_queryset(self):
        type = self.request.resolver_match.url_name
        model = apps.get_model(app_label='titles',
                               model_name=type.split('_')[0]).objects.all()
        model = filter_by_models(self.request, model)
        query = self.request.GET.get("q")
        if query:
            model = filter_by_name(query, model)
        model = model.values('id', 'title__original_name', 'image__thumbnail').annotate(
            relevance=Count('id')).order_by('-relevance', 'title__original_name')
        print(model)
        return model

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        type = self.request.resolver_match.url_name.split('_')[0]
        filter_dict = cache.get(f'filterdict:{type}')
        if filter_dict is None:
            if type == 'manga':
                list_models = {'Type': MangaType, 'Demographic': Demographic,
                               'Publisher': Publisher, 'Theme': Theme, 'Genre': Genre}
            elif type == 'anime':
                list_models = {'Type': AnimeType, 'Demographic': Demographic,
                               'Studio': Studio, 'Theme': Theme, 'Genre': Genre}
            filter_dict = {}
            for key, item in list_models.items():
                filter_dict[key] = item.objects.all().values(
                    'name').order_by('name')
            cache.set(f'filterdict:{type}', filter_dict)
        query = self.request.GET.get("q")
        context.update(
            {'filter': filter_dict, 'model': type.capitalize(), 'query': query})
        return context


class TitleDetail(TemplateResponseMixin, View):
    template_name = 'titles/detail_test.html'
    context_object_name = 'item'


    def get(self,request,pk):
        tab = self.request.GET.get('tab')
        if not tab:
            tab = 'info'
        key=f'titledetail:{tab}:{self.kwargs["pk"]}'
        model=cache.get(key)
        if model is None:
            type = self.request.resolver_match.url_name
            tab = self.request.GET.get('tab')
            if not tab:
                tab = 'info'
            model = apps.get_model(app_label='titles',
                                model_name=type.split('_')[0]
                                ).objects.filter(id=self.kwargs['pk']).annotate(
                **annotate_acc(type, tab)
                ).values(*values_acc(type, tab))
            cache.set(key,model)
        model1 = self.request.resolver_match.url_name.split('_')[0]
        tab = self.request.GET.get('tab')

        return self.render_to_response({'item':model,'model': model1, 'tab': tab, })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key=f'titledetail:{self.kwargs["pk"]}'
        model=cache.get(key)
        if model is None:
            type = self.request.resolver_match.url_name
            id = self.kwargs['pk']
            tab = self.request.GET.get('tab')
            if not tab:
                tab = 'info'
            model = apps.get_model(app_label='titles',
                                model_name=type.split('_')[0]
                                ).objects.filter(id=self.kwargs["pk"]).annotate(
                **annotate_acc(type, tab)
                ).values(*values_acc(type, tab))
            cache.set(key,model)
        model1 = self.request.resolver_match.url_name.split('_')[0]
        tab = self.request.GET.get('tab')
        context.update({'item':model,'model': model1, 'tab': tab, })
        return context
