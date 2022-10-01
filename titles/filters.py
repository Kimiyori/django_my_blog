
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import CharField, TextField
from django.db.models.functions import Cast
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Q, Value,QuerySet
from django.db.models.expressions import Func
from urllib.parse import urlsplit, parse_qs
from typing import Dict, List, Optional, Tuple, Type, Union
from django.http import HttpRequest
from django.apps import apps
from comments.models import CommentAnime, CommentManga
from titles.models import Anime, Manga


class Filter:
    """
    Calling class for filtering
    """
    def __call__(self, name: str, item: str) -> Dict[str, str]:
        return {
            f'{name}__name__icontains': item
        }


def filter_by_name(request: HttpRequest, item: QuerySet[Union[Manga, Anime]]) -> Tuple[QuerySet, Optional[str]]:
    """
    Function for filtering by title name if 'q' given in request.

    :param HttpRequest request: send request from main method to get q query param

    :param QuerySet item: Send QuerySet given instance to filter q=name

    """
    title_name: Optional[str] = request.GET.get('q')
    if title_name:
        item = item.filter(
            Q(title__original_name__icontains=title_name) |
            Q(title__russian_name__icontains=title_name) |
            Q(title__english_name__icontains=title_name))

    return (item, title_name)


class Array(Func):
    """
    Inplementation psql array func.
    """
    template = '%(function)s[%(expressions)s]'
    function = 'ARRAY'


def annotate_acc(type: str, tab: str) -> Dict[str,  ArrayAgg]:
    """
    Function for annotation that defines specific values.

    :param str type: Type title(manga or anime).

    :param str tab: info or related.
    """

    def create_wrapper(name: str) -> Union[Value, F, Cast]:
        # if name just anime or manga, then wrap in into Value() to pass original name into template.
        # This field is required to determine the type when referring 
        # to 'adapted' or 'based on' when it could be either anime or manga.
        if name in ['anime', 'manga']:
            return Value(name)
        # if not id field, use default F()
        elif name[-2:] != 'id':
            return F(name)
        # id cannot be converted in F because it uses uuid and for that we need cast func and convert it to string
        else:
            return Cast(F(name), output_field=TextField(max_length=40))

    def create_array(list: list[str]) -> ArrayAgg:
        # use default ArrayAgg for values
        if len(list) <= 1:
            arr = [create_wrapper(name) for name in list]
            r = ArrayAgg(*arr, distinct=True)
        # if values more that 1, then use psql Array func to wrap it
        else:
            arr = Array(*[create_wrapper(name) for name in list],
                        output_field=ArrayField(CharField(max_length=200)))
            r = ArrayAgg(arr, distinct=True)
        return r
    # dictionary with values for specific tab for certail title model
    d_anno = {'manga': {
                'info':
                    {'genres': ['genre__name'],
                    'publishers': ['publisher__name'],
                    'themes': ['theme__name'],
                    'magazines': ['magazine__name'],
                    'urls_list': ['urls__mal', 'urls__shiki', 'urls__manga_updates', 
                                    'urls__manga_dex', 'urls__manga_lib'],
                    'related_posts': ['related_post__id', 'related_post__title', 'related_post__main_image']
                    },
                'related':
                    {'adaptations': ['adaptation__adaptation__id', 'adaptation__adaptation__image__thumbnail', 
                                    'adaptation__adaptation__title__original_name', 'anime'],
                    'based_ons': ['based_on__based_on__id', 'based_on__based_on__image__thumbnail', 
                                    'based_on__based_on__title__original_name', 'anime'],
                    'sequels': ['sequel__sequel__id', 'sequel__sequel__image__thumbnail', 
                                'sequel__sequel__title__original_name'],
                    'prequels': ['prequel__prequel__id', 'prequel__prequel__image__thumbnail', 
                                    'prequel__prequel__title__original_name']
                    }
                        },
                            
            'anime': {
                'info':
                    {'genres': ['genre__name'],
                    'themes': ['theme__name'],
                    'studios': ['studio__name'],
                    'urls_list': ['urls__mal', 'urls__shiki', 'urls__anilist', 'urls__world_art'],
                    'related_posts': ['related_post__id', 'related_post__title', 'related_post__main_image']
                    },
                'related':
                    {'adaptations': ['adaptation__adaptation__id', 'adaptation__adaptation__image__thumbnail', 
                                    'adaptation__adaptation__title__original_name', 'manga'],
                    'based_ons': ['based_on__based_on__id', 'based_on__based_on__image__thumbnail', 
                                    'based_on__based_on__title__original_name', 'manga'],
                    'sequels': ['sequel__sequel__id', 'sequel__sequel__image__thumbnail', 
                                    'sequel__sequel__title__original_name'],
                    'prequels': ['prequel__prequel__id', 'prequel__prequel__image__thumbnail', 
                                    'prequel__prequel__title__original_name']
                                    }
                        }
            }
    # compile dict for annotate
    annotate_dict = {key: create_array(value)
                     for (key, value) in d_anno[type][tab].items()}
    return annotate_dict


def values_acc(type: str, tab: str) -> List[str]:
    """
    Simple func that serves as dict of values

    :param str type: Type title(manga or anime).

    :param str tab: info or related.
    """
    d_values = {'manga': {
                    'info': ['id', 'description', 'title__original_name', 'title__russian_name',
                            'title__english_name', 'type__name', 'authors__author__name', 
                            'authors__artist__name', 'premiere','volumes', 'chapters', 
                            'demographic__name', 'image__image', 'genres', 'publishers',
                                        'themes', 'magazines', 'related_posts', 'score', 'urls_list'],
                    'related': ['id', 'image__image', 'title__original_name', 'title__russian_name',
                                'title__english_name', 'adaptations', 'based_ons', 'sequels', 'prequels']
                        },

                'anime': {
                    'info': ['id', 'description', 'title__original_name', 'title__russian_name',
                             'title__english_name', 'type__name', 'premiere',
                             'episodes', 'image__image', 'genres', 'themes', 'studios', 
                             'related_posts', 'score', 'urls_list'],
                    'related': ['id', 'image__image', 'title__original_name', 'title__russian_name',
                                'title__english_name', 'adaptations', 'based_ons', 'sequels', 'prequels']
                        },
                }
    return d_values[type][tab]


def filter_by_models(
    request: HttpRequest,
    instance: QuerySet[Union[Manga, Anime]]
) -> Tuple[QuerySet[Union[Manga, Anime]], Dict[str, str]]:
    """
    Filter instance by its attributes.

    :param HttpRequest request: send request from main method to get q query param

    :param QuerySet item: Send QuerySet given instance to filter by given attributes
    """
    fil = Filter()
    # get attirubtes from query parameters
    params: Dict[str, List[str]] = parse_qs(
        urlsplit(request.get_full_path()).query)
    if 'page' in params:
        del params['page']
    if 'q' in params:
        del params['q']
    for model, list in params.items():
        for item in list:
            instance = instance.filter(**fil(name=model, item=item))
    return instance, params


def get_comments(type: str, id: int) -> Type[Union[CommentManga, CommentAnime|None]]:
    """
    Get comments for title instance
    """
    return apps.get_model(app_label='comments',
                          model_name=f'comment{type}'
                          ).objects.select_related('author__profile').filter(model=id)

def get_instance(model,type,tab,id):
    return model.objects.annotate(
                **annotate_acc(type, tab)
            ).values(*values_acc(type, tab)).get(id=id)