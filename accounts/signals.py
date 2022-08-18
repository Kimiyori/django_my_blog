from io import BytesIO
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from .models import CustomUser, Profile
THUMBNAIL_SIZE = (400,400)
# logging
file_logger = logging.getLogger('file_logger')
console_logger = logging.getLogger('console_logger')

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

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, **kwargs):
    if not hasattr(instance,'profile'):
        console_logger.info(f'Create profile for user with id {instance.id}')
        Profile.objects.create(user=instance)