
from typing import Any
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponse
from django.views.generic import ListView
from .models import Genre,  Demographic, AnimeType, MangaType, Publisher, Studio, Theme
import logging
from .filters import filter_by_name, annotate_acc, values_acc, filter_by_models
from django.core.cache import cache
from django.apps import apps
from django.views.generic.base import TemplateResponseMixin, View
from .paginator import LargeTablePaginator

# Create your views here.

file_logger=logging.getLogger('file_logger')
console_logger=logging.getLogger('console_logger')

class TitleList(ListView):
    """Get list of titles"""
    template_name = 'titles/list.html'
    context_object_name = 'list'
    paginate_by = 20
    paginator = LargeTablePaginator

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBadRequest:
        # get type of title (manga or anime)
        self.type = self.request.resolver_match.url_name.split('_')[0]
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> HttpResponse:
        console_logger.info(f'Trying to get list of {self.type}\'s')
        # get model based on type
        model = apps.get_model(app_label='titles',
                               model_name=self.type).objects.all()
        # filter instance based on attributes
        model,params = filter_by_models(self.request, model)
        # get q if need filter by title and then filter
        model,title_name = filter_by_name(self.request,  model)
        # optimize by taking only the necessary values and order it
        model = model.values('id', 'title__original_name',
                             'image__thumbnail').order_by('title__original_name')
        file_logger.info(f'Successfil get list of {self.type}',extra={'filers':params,'title_filter':title_name})
        return model

    def get_context_data(self, **kwargs) -> HttpResponse:
        context = super().get_context_data(**kwargs)
        # inicialize cache key for filter bar
        cache_key = f'filterdict:{self.type}'
        # check if in cache and if not, create filter_dict and put it in cache
        filter_dict = cache.get(cache_key)
        if filter_dict is None:
            list_models = {'Theme': Theme, 'Genre': Genre}
            if self.type == 'manga':
                list_models['Type'] = MangaType
                list_models['Demographic'] = Demographic
                list_models['Publisher'] = Publisher
            elif self.type == 'anime':
                list_models['Type'] = AnimeType
                list_models['Studio'] = Studio
            filter_dict = {}
            for key, item in list_models.items():
                filter_dict[key] = item.objects.all().values(
                    'name').order_by('name')
            cache.set(cache_key, filter_dict, 5*60)
        # get q from query string, using it for title search
        query = self.request.GET.get("q")
        # update context
        context.update({
            'filter': filter_dict,
            'model': self.type.capitalize(),
            'query': query})
        return context


class TitleDetail(TemplateResponseMixin, View):
    """Take a specific title instance"""
    template_name = 'titles/detail_test.html'
    context_object_name = 'item'

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        # get tab(info or related,depending of query params)
        tab = self.request.GET.get('tab')
        # check if tab params is empty; if its empty, then assign it default 'info' value
        if not tab:  
            tab = 'info'
         # get type if url(anime or manga)
        type = self.request.resolver_match.url_name.split('_')[0] 
        console_logger.info(f'Trying get detail about {type} with id {pk}')
        key = f'titledetail:{tab}:{self.kwargs["pk"]}'  # create cache key
        model = cache.get(key)
        # if got in cache, then create queryset in cache it
        if model is None: 
            # get info from model based on type and tab
            model = apps.get_model(app_label='titles',
                                   model_name=type
                                   ).objects.filter(id=self.kwargs['pk']).annotate(
                **annotate_acc(type, tab)
            ).values(*values_acc(type, tab))
            cache.set(key, model, 5*60)  # cache queryset
        console_logger.info(f'Successful get detail about {type} with id {pk}')
        return self.render_to_response({'item': model, 'model': type, 'tab': tab, })
