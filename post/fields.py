from django.db import models
from django.core.exceptions import ObjectDoesNotExist
class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)
    def pre_save(self, model_instance, add):
        if model_instance.pk is  None:
            qs = self.model.objects.all()
            if self.for_fields:
                query = {field: getattr(model_instance, field) for field in self.for_fields}
                qs = qs.filter(**query)
                cur_max=int(model_instance.order)
                for item in qs:
                    if (item.order - cur_max) in [0,1]:
                        cur_max=item.order
                        value=item.order+1
                        setattr(item, self.attname, value)
                        item.save()
            return int(model_instance.order)   
        else:
            return super().pre_save(model_instance, add)