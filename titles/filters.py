from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .models import Manga,Anime
class Filter:
    def __call__(self,name:str,item):
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

    