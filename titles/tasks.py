from celery import shared_task
from .models import Anime,Manga
from .api_urls import myanimelist
import re 
from django.core.exceptions import ValidationError
import logging
from django.apps import apps


file_logger=logging.getLogger('file_logger')
console_logger=logging.getLogger('console_logger')


@shared_task
def add_score(id,type):
    console_logger.info(f'Get score for {type} with id {id}')
    api=myanimelist.log()
    instance=apps.get_model(app_label='titles',
                               model_name=type).objects.get(id=id)
    mal_id=re.findall(f'https://myanimelist.net/{type}/(\d+)/',instance.urls.mal)[0]
    if type=='anime':
        score=api.anime(int(mal_id)).GET(fields='mean').get('mean',0)
    elif type=='manga':
        score=api.manga(int(mal_id)).GET(fields='mean').get('mean',0)
    else:
        file_logger.debug(f'error when adding score to a title because type of a title is invalid')
        return ValidationError('Not correct type of title')
    instance.score=score
    instance.save()
    console_logger.info(f'Succeessfull set score for {type} with id {id}')
    return score

@shared_task
def update_anime_scores():
    api=myanimelist.log()
    anime_list=Anime.objects.select_related('urls')
    updated_list=[]
    for anime in anime_list.iterator():

        if anime.urls and anime.urls.mal:
            mal_id=re.findall(f'https://myanimelist.net/anime/(\d+)/',anime.urls.mal)[0]
            score=anime.score
            upd_score=api.anime(int(mal_id)).GET(fields='mean').get('mean',0)
            if score!=upd_score:
                anime.score=upd_score
                updated_list.append(anime)
    Anime.objects.bulk_update(updated_list,['score'])


@shared_task
def update_manga_scores():
    api=myanimelist.log()
    manga_list=Manga.objects.select_related('urls')
    updated_list=[]
    for manga in manga_list.iterator():
        if manga.urls and manga.urls.mal:
            mal_id=re.findall(f'https://myanimelist.net/manga/(\d+)/',manga.urls.mal)[0]
            score=manga.score
            upd_score=api.manga(int(mal_id)).GET(fields='mean').get('mean',0)
            if score!=upd_score:
                manga.score=upd_score
                updated_list.append(manga)
    Manga.objects.bulk_update(updated_list,['score'])