from typing import Any, NoReturn
from django.apps import apps
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.db.models import QuerySet

file_logger = logging.getLogger('file_logger')


class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args:Any, **kwargs:Any):
        #reference to post model
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance:QuerySet,add:bool)->NoReturn:
            try:
                #content model
                qs= self.model.objects.all()
                if self.for_fields:
                    query = {field: getattr(model_instance, field)
                             for field in self.for_fields}
                    qs = qs.filter(**query)
                    if getattr(model_instance, self.attname) is not None:
                        cur_max = getattr(model_instance,self.attname)
                        for item in qs:
                            if item.order - cur_max==0:
                                value = getattr(item,self.attname)+1
                                cur_max = value
                                setattr(item, self.attname, value)
                        content=apps.get_model(app_label='post',model_name='content')
                        content.objects.bulk_update(qs,['order'])

                    else:
                        try:
                            last_item = qs.last(self.attname)
                            value = last_item.order + 1
                        except ObjectDoesNotExist:
                            value = 1
                        setattr(model_instance, self.attname, value)

            except Exception as e:
                file_logger.warning(f'Can\'t update content order because of the following error - {e}')
            return model_instance.order

