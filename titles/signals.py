from io import BytesIO
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Image as ImageTable
from .models import Anime,Manga
from .api_urls import myanimelist
import re 
from django.core.exceptions import ValidationError
THUMBNAIL_SIZE = (400, 400)
file_logger=logging.getLogger('file_logger')
console_logger=logging.getLogger('console_logger')


@receiver(pre_save, sender=ImageTable)
def generate_thumbnail(sender, instance, **kwargs):
    """Generate thumbnail when upload image"""
    #if image, then create or recreate thumbnail
    if instance.image:
        file_logger.info(
        "Generating thumbnail for  %d",
        instance.image,
        )
        image = Image.open(instance.image)
        image = image.convert("RGB")
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        temp_thumb = BytesIO()
        image.save(temp_thumb, "JPEG")
        temp_thumb.seek(0)
        instance.thumbnail.save(
        instance.image.name,
        ContentFile(temp_thumb.read()),
        save=False,
        )
        temp_thumb.close()
        file_logger.info(
        "Successful generate thumbnail for  %d",
        instance.image,
        )
    # case for delete. if thumbnail exist, but not image, then delete thumbnail too
    elif instance.thumbnail and not instance.image:
        file_logger.info(
        "Delete thumbnail for  %d",
        instance.image,
        )
        instance.thumbnail.delete()
        file_logger.info(
        "Successful delete thumbnail for  %d",
        instance.image,
        )

@receiver(pre_save, sender=Manga)
@receiver(pre_save, sender=Anime)
def get_score_for_title(sender,instance,**kwargs):
    type='anime' if isinstance(instance,Anime) else 'manga'
    console_logger.info(f'Get score for {type} with id {instance.id}')
    api=myanimelist.log()
    mal_id=re.findall(f'https://myanimelist.net/{type}/(\d+)/',instance.urls.mal)[0]
    if type=='anime':
        score=api.anime(int(mal_id)).GET(fields='mean')['mean']
    elif type=='manga':
        score=api.manga(int(mal_id)).GET(fields='mean')['mean']
    else:
        file_logger.debug(f'error when adding score to title because type of title is invalid')
        return ValidationError('Not correct type of title')
    setattr(instance,'score',score)
    console_logger.info(f'Succeessfull set score for {type} with id {instance.id}')
