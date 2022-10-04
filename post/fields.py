from typing import Any, Sequence, Union, TYPE_CHECKING
from django.apps import apps
from django.db import models
import logging
from django.db.models import QuerySet

if TYPE_CHECKING:
    from .models import Post, Content


file_logger = logging.getLogger("file_logger")


class OrderField(models.PositiveIntegerField):
    def __init__(
        self, for_fields: Union[Sequence[str], None] = None, *args: Any, **kwargs: Any
    ):
        # reference to post model
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add: bool):
        try:
            # list all contents instances
            qs: QuerySet[Content] = self.model.objects.all()
            if self.for_fields:
                # {'post':<Post>} get post foe given content instance for filter
                query: dict[str, Post] = {
                    field: getattr(model_instance, field) for field in self.for_fields
                }
                # get all contents for given post
                qs = qs.filter(**query)
                if getattr(model_instance, self.attname) is not None:
                    cur_max = getattr(model_instance, self.attname)
                    for item in qs:
                        if item != model_instance and item.order > cur_max:
                            setattr(item, self.attname, cur_max + 1)
                            cur_max += 1
                        elif item.order == cur_max:
                            value = getattr(item, self.attname) + 1
                            cur_max = value
                            setattr(item, self.attname, value)
                    content = apps.get_model(app_label="post", model_name="content")
                    content.objects.bulk_update(qs, ["order"])

                else:
                    try:
                        last_item = qs.last()
                        value = last_item.order + 1
                    except AttributeError:
                        value = 1
                    setattr(model_instance, self.attname, value)
            return model_instance.order
        except Exception as e:
            file_logger.warning(
                f"Can't update content order because of the following error - {e}"
            )
            raise e
