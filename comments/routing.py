from django.urls import re_path,path
from . import consumers


websocket_urlpatterns=[
    path(r'post/<id>/',consumers.PostCommentsConsumer.as_asgi()),
    path(r'manga/<uuid:id>/',consumers.PostCommentsConsumer.as_asgi()),
    path(r'anime/<uuid:id>/',consumers.PostCommentsConsumer.as_asgi()),

]