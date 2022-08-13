from django.urls import re_path,path
from . import consumers


websocket_urlpatterns=[
    re_path(r'(manga|anime|post)/(?P<id>[a-zA-Z0-9-]+)/',consumers.PostCommentsConsumer.as_asgi())

]