import json
from typing import Dict, Union
from django.apps import apps
from django.http import Http404
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from post.models import Post
from .models import CommentPost
import redis
from django.conf import settings
import re
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
class PostCommentsConsumer(AsyncWebsocketConsumer):


    async def connect(self):
        self.model_type = re.search(r'^\/(\w+)\/', self.scope['path']).group(1)
        self.id = self.scope['url_route']['kwargs']['id']
        self.post_group_name = f'{self.model_type}_{self.id}'
        await self.channel_layer.group_add(
            self.post_group_name,
            self.channel_name
        )
        self.comment_model = apps.get_model(app_label='comments',
                                            model_name=f'comment{self.model_type}')

        if self.model_type == 'post':
            self.model = Post
        else:
            self.model = apps.get_model(app_label='titles',
                                        model_name=self.model_type)
        self.r = redis.Redis(host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        db=settings.REDIS_DB)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.post_group_name,
            self.channel_name
        )

    async def receive(self, text_data: Union[str, bytes]):
        text_json_load = json.loads(text_data)
        if text_json_load['type'] == 'increment_views':
            new_comment = await self.increment()
        elif text_json_load['type'] == 'new_comment':
            new_comment = await self._new_comment(text_json_load)
        elif text_json_load['type'] == 'delete_comment':
            new_comment = await self._delete_comment(text_json_load)
        else:
            raise ValueError
        await self.channel_layer.group_send(
            self.post_group_name,
            {
                'type': text_json_load['type'],
                'message': new_comment
            }
        )

    async def increment_views(self, event):
        message = event['message']
        await self.send(
            text_data=json.dumps({
                'type': 'increment_views',
                'message': message
            })
        )

    async def new_comment(self, event):
        message = event['message']
        await self.send(
            text_data=json.dumps({
                'type': 'new_comment',
                'message': message
            })
        )

    async def delete_comment(self, event):
        message = event['message']
        await self.send(
            text_data=json.dumps({
                'type': 'delete_comment',
                'message': message
            })
        )

    @database_sync_to_async
    def _new_comment(self, data: Dict[str, str]) -> Dict[str, Union[str, int]]:
        get_parent = data.get('parent', None)
        try:
            parent = self.comment_model.objects.get(
            id=get_parent) if get_parent else None
        except self.comment_model.DoesNotExist:
            raise ObjectDoesNotExist
        try:
            user=get_user_model().objects.get(id=data['author'])
        except get_user_model().DoesNotExist:
            raise ObjectDoesNotExist
        try:
            new_comment = self.comment_model.objects.create(
                model=self.model.objects.get(id=self.id),
                parent=parent,
                author=user,
                content=data['content']
            )
        except IntegrityError:
            raise IntegrityError
    
        return {
            'id': new_comment.id,
            'author_id': new_comment.author.id,
            'author': new_comment.author.username,
            'author_image': str(new_comment.author.profile.photo),
            'parent': str(getattr(new_comment.parent, 'id', None)),
            'content': new_comment.content,
            'created': new_comment.created.strftime("%b %d %H:%M")

        }

    @database_sync_to_async
    def _delete_comment(self, data: Dict[str, str]) -> Dict[str, Union[str, int]]:
        try:
            comment = self.comment_model.objects.get(id=data['comment_id'])
            comment.delete()
            data = {
                'id': data['comment_id']
            }
            return data
        except self.comment_model.DoesNotExist:
            raise ObjectDoesNotExist


    @database_sync_to_async
    def increment(self):
        # increate in redis number of views in post
        total_views = self.r.incr(f'post:{self.id}:views')

        return {
            'count': total_views
        }
