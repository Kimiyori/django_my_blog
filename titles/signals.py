import logging
from typing import Any
from django.db.models.signals import post_delete
from django.dispatch import receiver
import shutil
from .models import Image as ImageTable
import re
from django.db.models import QuerySet
from typing import  Any, NoReturn
import re


#logger
file_logger = logging.getLogger('file_logger')
console_logger = logging.getLogger('console_logger')

THUMBNAIL_SIZE = (400, 400)
    
@receiver(post_delete, sender=ImageTable)
def delete_files(sender: Any, instance: QuerySet, **kwargs: Any) -> NoReturn:

    a=re.search(r'^(.+/)original/',instance.image.path).group(1)
    try:
        shutil.rmtree(a)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
