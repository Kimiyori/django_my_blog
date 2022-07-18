import json
from typing import Dict, Union

from django.http import Http404
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from post.models import Comment, Post
import redis
from django.conf import settings

class CommentsConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.post_group_name = 'post_%s' % self.post_id
        await self.channel_layer.group_add(
            self.post_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.post_group_name,
            self.channel_name
        )

    async def receive(self, text_data:Union[str, bytes]):
        text_json_load = json.loads(text_data)
        if text_json_load['type'] == 'increment_views':
            new_comment = await self.increment()
        elif text_json_load['type'] == 'new_comment':
            new_comment = await self.create_new_comment(text_json_load)
        elif text_json_load['type'] == 'delete_comment':
            new_comment = await self._delete_comment(text_json_load)
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
    def create_new_comment(self, data:Dict[str,str])->Dict[str,Union[str,int]]:
        get_parent=data.get('parent', None)
        parent = Comment.objects.get(id=get_parent) if get_parent else None

        new_comment = Comment.objects.create(
            post=Post.objects.get(id=self.post_id),
            parent=parent,
            author=self.scope['user'],
            content=data['content']
        )
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
    def _delete_comment(self, data:Dict[str,str])->Dict[str,Union[str,int]]:
        try:
            comment = Comment.objects.get(id=data['comment_id'])
            comment.delete()
            data={
                'id': data['comment_id']
            }
        except Comment.DoesNotExist:
            data=data={
                'id': f"Cannot find comment with given id {data['comment_id']}"
            }
        return data

    @database_sync_to_async
    def increment(self):
        r = redis.Redis(host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        db=settings.REDIS_DB)
        # increate in redis number of views in post
        total_views = r.incr(f'post:{self.post_id}:views')

        return {
            'count':total_views
            }