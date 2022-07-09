from django.urls import re_path,path
from . import consumers


websocket_urlpatterns=[
    path(r'post/<post_id>/',consumers.CommentsConsumer.as_asgi()),
]