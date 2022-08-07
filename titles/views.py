
from typing import Any, Dict, Optional, Type, Union
from django.http import Http404, HttpRequest, HttpResponseBadRequest, HttpResponse
from django.views.generic import ListView

from comments.forms import CommentForm
from .models import Anime, Genre,  Demographic, AnimeType, Manga, MangaType, Publisher, Studio, Theme, Urls
import logging
from .filters import filter_by_name, annotate_acc, get_comments, values_acc, filter_by_models
from django.core.cache import cache
from django.apps import apps
from django.views.generic.base import TemplateResponseMixin, View
from .paginator import LargeTablePaginator
from django.db.models import QuerySet

# logging
file_logger = logging.getLogger('file_logger')
console_logger = logging.getLogger('console_logger')
CACHE_TIME = 60*5


class TitleList(ListView):
    """
    Get list of titles
    """
    template_name = 'titles/list.html'
    context_object_name = 'list'
    paginate_by = 20
    paginator = LargeTablePaginator

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # get type of title (manga or anime)
        self.type: str = self.request.resolver_match.url_name.split('_')[0]
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Union[Manga, Anime]]:
        console_logger.info(f'Trying to get list of {self.type}\'s')
        # get model based on type
        model: Type[Anime | Manga] = apps.get_model(app_label='titles',
                                                    model_name=self.type).objects.all()
        # filter instance based on attributes
        model, params = filter_by_models(request=self.request, instance=model)
        # get q if need filter by title and then filter
        model, title_name = filter_by_name(request=self.request,  item=model)

        model = model.values('id', 'title__original_name',
                             'image__thumbnail').order_by('title__original_name')
        console_logger.info(f'Successfil get list of {self.type}', extra={
                            'filers': params, 'title_filter': title_name})
        return model

    def get_context_data(self, **kwargs: Any) -> HttpResponse:
        context: dict = super().get_context_data(**kwargs)
        # inicialize cache key for filter bar
        cache_key: str = f'filterdict:{self.type}'
        # check if in cache and if not, create filter_dict and put it in cache
        filter_dict: str = cache.get(cache_key)
        if filter_dict is None:
            filter_list_models: Dict[str, Dict[str, QuerySet]] = {'manga':
                                                                  {'Theme': Theme, 'Genre': Genre, 'Type': MangaType,
                                                                   'Demographic': Demographic, 'Publisher': Publisher},
                                                                  'anime':
                                                                  {'Theme': Theme, 'Genre': Genre,
                                                                   'Type': AnimeType, 'Studio': Studio}}
            filter_dict: Dict[str, QuerySet] = {}
            for key, item in filter_list_models[self.type].items():
                filter_dict[key] = item.objects.all().values(
                    'name').order_by('name')
            cache.set(cache_key, filter_dict, CACHE_TIME)
        # get q from query string, using it for title search
        query: str = self.request.GET.get("q")
        # update context
        context.update({
            'filter': filter_dict,
            'model': self.type.capitalize(),
            'query': query})
        return context


class TitleDetail(TemplateResponseMixin, View):
    """
    Take a specific title instance
    """
    template_name = 'titles/detail_test.html'
    context_object_name = 'item'

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        # get tab(info or related,depending of query params)
        tab: str = self.request.GET.get('tab', 'info')
        # get type if url(anime or manga)
        type: str = self.request.resolver_match.url_name.split('_')[0]
        console_logger.info(f'Trying get detail about {type} with id {pk}')
        key: str = f'titledetail:{tab}:{self.kwargs["pk"]}'  # create cache key
        model: Optional[str] = cache.get(key)
        # if got in cache, then create queryset in cache it
        if model is None:
            # get info from model based on type and tab
            model = apps.get_model(app_label='titles',
                                   model_name=type
                                   ).objects.annotate(
                **annotate_acc(type, tab)
            ).values(*values_acc(type, tab)).get(id=self.kwargs['pk'])
            if not model:
                raise Http404('Cannot find title with given id')
            cache.set(key, model, CACHE_TIME)  # cache queryset
        comments = get_comments(type, pk)
        comment_form=CommentForm(apps.get_model(app_label='comments',
                                   model_name=f'comment{type}'
                                   ))
        console_logger.info(f'Successful get detail about {type} with id {pk}')
        return self.render_to_response({'item': model,
                                        'model': type,
                                        'tab': tab,
                                        'comments': comments,
                                        'comment_form': comment_form,})
