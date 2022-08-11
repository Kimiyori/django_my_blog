
from inspect import getargvalues
import logging
from typing import Any, NoReturn

from django.db.models.signals import pre_save,post_delete,pre_delete
from django.dispatch import receiver
from django.db.models import QuerySet
from post.models import Content
THUMBNAIL_SIZE = (400, 400)

file_logger = logging.getLogger('file_logger')
console_logger = logging.getLogger('console_logger')

    
@receiver(post_delete, sender=Content)
def delete_files(sender: Any, instance: QuerySet, **kwargs: Any) -> NoReturn:
    remaining_content=instance.post.contents.all()
    min_order=1
    for content in remaining_content:
        order=getattr(content,'order')
        if order-min_order>0:
            setattr(content,'order',min_order)
            content.save()
            break
        min_order+=1
    
    
    