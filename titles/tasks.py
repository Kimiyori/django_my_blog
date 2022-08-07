from celery import shared_task
from .models import Anime, Manga
from .api_urls import myanimelist
import re
from django.core.exceptions import ValidationError
import logging
from django.apps import apps
from uuid import UUID
from typing import  List,  Optional, Any,NoReturn,Type

# logging
file_logger = logging.getLogger('file_logger')
console_logger = logging.getLogger('console_logger')


def is_valid_uuid(val: str|int)-> bool:
    """
    Check if given val is valid UUID instance
    """
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False


class CustomError(Exception):
    pass


@shared_task
def add_score(id: UUID, type: str) -> Optional[int]:
    """
    Set score for given id title from myanimelist with mal api.

    :param uuid.UUID id: Send UUID to connect with instance.

    :param string type: Send only anime or manga type.
    """
    if type not in ['anime', 'manga']:
        raise ValueError('Incorrect type of title, only manga or anime')
    if not is_valid_uuid(id):
        raise ValueError('Incorrect type if id,needed UUID')

    model:Type[Anime | Manga] = apps.get_model(app_label='titles',
                           model_name=type)
    try:
        instance = model.objects.get(id=id)
    except model.DoesNotExist:
        raise ValueError('Did not find an instance for given id')
    if not getattr(instance, 'score'):
        if getattr(instance, 'urls') and getattr(instance.urls, 'mal'):
            try:
                mal_id: str = re.findall(
                    f'https://myanimelist.net/{type}/(\d+)/', instance.urls.mal)[0]
            except IndexError:
                file_logger.debug(f"""Error due to the fact that the link from the {type} instance 
                                    with gived id {id} and existing urls.mal could not be parsed 
                                    with link reference to get id""")
                raise IndexError('Could not parse urls.mal to get id')
            # log in mal api
            api: Type[myanimelist.MyAnimeList]= myanimelist.log()
            if type == 'anime':
                score:int = api.anime(int(mal_id)).GET(
                    fields='mean').get('mean', 0)
            elif type == 'manga':
                score:int = api.manga(int(mal_id)).GET(
                    fields='mean').get('mean', 0)
            else:
                file_logger.debug(
                    f'error when adding score to a title because type of a title is invalid')
                raise ValidationError('Not correct type of title')
            instance.score = score
            instance.save()
            console_logger.info(
                f'Succeessfull set score for {type} with id {id}')
            return score
        else:
            file_logger.debug(f"""{type.capitalize()} instance with following id {id} does not have 
                                    either urls field or urls.mal field""")
            raise AttributeError(
                'Instance doesnt have either urls field or urls.mal field')
    else:
        raise CustomError('Instance already has score')


@shared_task
def update_scores(type:str)-> NoReturn:
    """
    Scheduled task function to update scores.
    
    :param string type: Send only anime or manga type
    """

    if type not in ['anime', 'manga']:
        raise ValueError('Incorrect type of title, only manga or anime')

    model:Type[Anime | Manga] = apps.get_model(app_label='titles',
                           model_name=type)
    # log mal api
    api = myanimelist.log()
    updated_list: List[model] = []
    for title in model.objects.all():
        if getattr(title ,'urls') and getattr(title.urls,'mal'):
            try:
                mal_id: str= re.findall(
                    f'https://myanimelist.net/{type}/(\d+)/', title.urls.mal)[0]
            except IndexError:
                file_logger.debug(f"""Error due to the fact that the link from the {type} instance 
                                    with gived id {title.id} and existing urls.mal could not be parsed 
                                    with link reference to get id""")
                continue
            score :int= getattr(title,'score',0)
            if type=='anime':
                upd_score:int= api.anime(int(mal_id)).GET(
                    fields='mean').get('mean', 0)
            elif type=='manga':
                upd_score: int= api.manga(int(mal_id)).GET(
                    fields='mean').get('mean', 0)
            if int(score) != int(upd_score):
                title.score = upd_score
                updated_list.append(title)
        else:
            file_logger.debug(f'{type.capitalize()} with id {title.id} doesnt have either urls or urls.mal')
    model.objects.bulk_update(updated_list, ['score'])
    file_logger.info(f'Updated {type} scores for {len(updated_list)} instances')
