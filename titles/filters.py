from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .models import Manga,Anime
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields import CharField,UUIDField,TextField
from django.db.models.functions import Cast
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F
from django.db.models.expressions import Func
class Filter:
    def __call__(self,name:str,item)-> str:
        return {
            f'{name}__name__icontains':item
        }

def filter_by_name(query,item):
    search_vector = SearchVector('title__original_name', 'title__russian_name', 'title__english_name')
    search_query = SearchQuery(query)
    return item.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)
    ).filter(search=search_query).order_by("-rank")


class Array(Func):
    template = '%(function)s[%(expressions)s]'
    function = 'ARRAY'

def annotate_acc(type,tab)-> dict:
    def f_value(name):
        if name[-2:]!='id':
            return F(name)
        else:
            return Cast(F(name),output_field=TextField(max_length=40))
    def lst(list):
        if len(list)<=1:
            arr=[f_value(name) for name in list]
            r=ArrayAgg(*arr,distinct=True)
        else:
            arr=Array(*[f_value(name) for name in list],output_field=ArrayField(CharField(max_length=200)))
            r=ArrayAgg(arr,distinct=True)
        return r
    d_anno={'manga_detail':{
                            'info':
                                    {'genres':['genre__name'],
                                    'publishers':['publisher__name'],
                                    'themes':['theme__name'],
                                    'magazines':['magazine__name'],
                                    'related_posts':['related__post__id','related__post__title','related__post__main_image']},
                            'related':
                                    {'adaptations':['adaptation__adaptation__id','adaptation__adaptation__image','adaptation__adaptation__title__original_name'],
                                    'based_ons':['based_on__based_on__id','based_on__based_on__image','based_on__based_on__title__original_name'],
                                    'sequels':['sequel__sequel__id','sequel__sequel__image','sequel__sequel__title__original_name'],
                                    'prequels':['prequel__prequel__id','prequel__prequel__image','prequel__prequel__title__original_name']}},
            'anime_detail':{
                            'info':
                                    {'genres':['genre__name'],
                                    'themes':['theme__name'],
                                    'studios':['studio__name'],
                                    'related_posts':['related__post__id','related__post__title','related__post__main_image']},
                            'related':
                                    {'adaptations':['adaptation__adaptation__id','adaptation__adaptation__image','adaptation__adaptation__title__original_name'],
                                    'based_ons':['based_on__based_on__id','based_on__based_on__image','based_on__based_on__title__original_name'],
                                    'sequels':['sequel__sequel__id','sequel__sequel__image','sequel__sequel__title__original_name'],
                                    'prequels':['prequel__prequel__id','prequel__prequel__image','prequel__prequel__title__original_name']}
                    },
            
    }
    annotate_dict={key:lst(value) for (key,value) in d_anno[type][tab].items()}
    return annotate_dict

def values_acc(type,tab):
    d_values={'manga_detail':{
                            'info':['id','description','title__original_name', 'title__russian_name',
                                    'title__english_name','type__name','authors__author__name','authors__artist__name','premiere',
                                    'volumes','chapters','demographic__name','image','genres','publishers','themes','magazines','related_posts'],
                            'related':['id','image','title__original_name', 'title__russian_name',
                                        'title__english_name','adaptations','based_ons','sequels','prequels']},
                    'anime_detail':{
                                'info':['id','description','title__original_name', 'title__russian_name',
                                        'title__english_name','type__name','premiere',
                                        'episodes','image','genres','themes','studios','related_posts'],
                                'related':['id','image','title__original_name', 'title__russian_name',
                                        'title__english_name','adaptations','based_ons','sequels','prequels']},
                    }
    return d_values[type][tab]