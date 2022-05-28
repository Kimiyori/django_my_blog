
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import CharField, TextField
from django.db.models.functions import Cast
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Q,Value
from django.db.models.expressions import Func


class Filter:
    def __call__(self, name: str, item) -> str:
        return {
            f'{name}__name__icontains': item
        }


def filter_by_name(query, item):
    return item.filter(Q(title__original_name__icontains=query) | Q(title__russian_name__icontains=query) | Q(title__english_name__icontains=query))


class Array(Func):
    template = '%(function)s[%(expressions)s]'
    function = 'ARRAY'


def annotate_acc(type, tab) -> dict:
    def f_value(name):
        if 'anime' in name or 'manga' in name:
            return Value(name)
        elif name[-2:] != 'id':
            return F(name)
        else:
            return Cast(F(name), output_field=TextField(max_length=40))

    def lst(list):
        if len(list) <= 1:
            arr = [f_value(name) for name in list]
            r = ArrayAgg(*arr, distinct=True)

        else:
            arr = Array(*[f_value(name) for name in list],
                        output_field=ArrayField(CharField(max_length=200)))
            print(arr)
            r = ArrayAgg(arr, distinct=True)
        return r
    d_anno = {'manga_detail': {
        'info':
        {'genres': ['genre__name'],
         'publishers': ['publisher__name'],
         'themes': ['theme__name'],
         'magazines': ['magazine__name'],
         'related_posts': ['related__post__id', 'related__post__title', 'related__post__main_image']},
        'related':
        {'adaptations': ['adaptation__adaptation__id', 'adaptation__adaptation__image__thumbnail', 'adaptation__adaptation__title__original_name','anime'],
         'based_ons': ['based_on__based_on__id', 'based_on__based_on__image__thumbnail', 'based_on__based_on__title__original_name', 'anime'],
         'sequels': ['sequel__sequel__id', 'sequel__sequel__image__thumbnail', 'sequel__sequel__title__original_name'],
         'prequels': ['prequel__prequel__id', 'prequel__prequel__image__thumbnail', 'prequel__prequel__title__original_name']}},
        'anime_detail': {
        'info':
        {'genres': ['genre__name'],
         'themes': ['theme__name'],
         'studios': ['studio__name'],
         'related_posts': ['related__post__id', 'related__post__title', 'related__post__main_image']},
        'related':
        {'adaptations': ['adaptation__adaptation__id', 'adaptation__adaptation__image__thumbnail', 'adaptation__adaptation__title__original_name', 'manga'],
         'based_ons': ['based_on__based_on__id', 'based_on__based_on__image__thumbnail', 'based_on__based_on__title__original_name', 'manga'],
         'sequels': ['sequel__sequel__id', 'sequel__sequel__image__thumbnail', 'sequel__sequel__title__original_name'],
         'prequels': ['prequel__prequel__id', 'prequel__prequel__image__thumbnail', 'prequel__prequel__title__original_name']}
    },

    }

    annotate_dict = {key: lst(value)
                     for (key, value) in d_anno[type][tab].items()}
    return annotate_dict


def values_acc(type, tab):
    d_values = {'manga_detail': {
        'info': ['id', 'description', 'title__original_name', 'title__russian_name',
                 'title__english_name', 'type__name', 'authors__author__name', 'authors__artist__name', 'premiere',
                 'volumes', 'chapters', 'demographic__name', 'image__image', 'genres', 'publishers', 'themes', 'magazines', 'related_posts'],
        'related': ['id', 'image__image', 'title__original_name', 'title__russian_name',
                    'title__english_name', 'adaptations', 'based_ons', 'sequels', 'prequels']},
                'anime_detail': {
        'info': ['id', 'description', 'title__original_name', 'title__russian_name',
                 'title__english_name', 'type__name', 'premiere',
                                        'episodes', 'image__image', 'genres', 'themes', 'studios', 'related_posts'],
        'related': ['id', 'image__image', 'title__original_name', 'title__russian_name',
                    'title__english_name', 'adaptations', 'based_ons', 'sequels', 'prequels']},
                }
    return d_values[type][tab]


def filter_by_models(request, type, instance):
    fil = Filter()
    if type == 'manga_list':
        list_filter = ['genre', 'theme', 'demographic',
                       'type', 'publisher', 'magazine', ]
    elif type == 'anime_list':
        list_filter = ['genre', 'theme', 'type', 'studio']
    for model in list_filter:
        list = request.GET.getlist(model)
        if list:
            for item in list:
                instance = instance.filter(**fil(name=model, item=item))
    return instance
