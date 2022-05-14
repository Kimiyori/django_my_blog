from io import BytesIO
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Image as ImageTable
THUMBNAIL_SIZE = (400, 400)
logger = logging.getLogger(__name__)
@receiver(pre_save, sender=ImageTable)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info(
    "Generating thumbnail for product %d",
    instance.id,
    )
    if instance.image:
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
    elif instance.thumbnail and not instance.image:
        instance.thumbnail.delete()
