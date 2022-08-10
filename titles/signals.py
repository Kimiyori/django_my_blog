from io import BytesIO
import logging
from typing import Any
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save,post_delete,pre_delete
from django.dispatch import receiver
from django.db.models import FileField
from django.core.files.storage import default_storage
import shutil
from titles.tasks import add_score
from .models import Image as ImageTable
from .models import Anime, Manga
from .api_urls import myanimelist
import re
from django.db.models import QuerySet
from typing import List,  Optional, Any, NoReturn, Type
from django.core.exceptions import ValidationError
import os
import re
THUMBNAIL_SIZE = (400, 400)

file_logger = logging.getLogger('file_logger')
console_logger = logging.getLogger('console_logger')


# #@receiver(pre_save, sender=ImageTable)
# def generate_thumbnail(sender: Any, instance: QuerySet, **kwargs: Any) -> NoReturn:
#     """
#     Generate thumbnail when upload image

#     :param Any sender: Image model

#     :param QuerySet instance: Send QuerySet intance for access to attrs
#     """

#     # if image, then create or recreate thumbnail
#     if instance.image:
#         console_logger.info("Generating thumbnail for  %d", instance.id,)
#         image = Image.open(instance.image)
#         image = image.convert("RGB")
#         image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
#         temp_thumb = BytesIO()
#         image.save(temp_thumb, "JPEG")
#         temp_thumb.seek(0)
#         instance.thumbnail.save(
#             instance.image.name,
#             ContentFile(temp_thumb.read()),
#             save=False,
#         )
#         temp_thumb.close()
#         file_logger.info(
#             "Successful generate thumbnail for  %d",
#             instance.id,
#         )
#     # case for delete. if thumbnail exist, but not image, then delete thumbnail too
#     elif instance.thumbnail and not instance.image:
#         console_logger.info(
#             "Delete thumbnail for  %d",
#             instance.id,
#         )
#         instance.thumbnail.delete()
#         file_logger.info(
#             "Successful delete thumbnail for  %d",
#             instance.id,
#         )
    
@receiver(post_delete, sender=ImageTable)
def delete_files(sender: Any, instance: QuerySet, **kwargs: Any) -> NoReturn:

    a=re.search(r'^(.+/)original/',instance.image.path).group(1)
    try:
        shutil.rmtree(a)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
