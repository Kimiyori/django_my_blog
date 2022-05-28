from io import BytesIO
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Profile
THUMBNAIL_SIZE = (400,400)

@receiver(pre_save, sender=Profile)
def generate_thumbnail(sender, instance, **kwargs):

    if instance.photo:
        image = Image.open(instance.photo)
        image = image.convert("RGB")
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        temp_thumb = BytesIO()
        image.save(temp_thumb, "JPEG")
        temp_thumb.seek(0)
        instance.photo.save(
        instance.photo.name,
        ContentFile(temp_thumb.read()),
        save=False,
        )
        temp_thumb.close()