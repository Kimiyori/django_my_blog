import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from post.models import Comment, Post


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
        await self.channel_layer.discard(
            self.post_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_json_load = json.loads(text_data)
        if text_json_load['type'] == 'new_comment':
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
    def create_new_comment(self, data):
        if data.get('parent', None):
            parent = Comment.objects.get(id=data.get('parent', None))
        else:
            parent = None
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
            'parent': getattr(new_comment.parent, 'id', None),
            'content': new_comment.content,
            'created': new_comment.created.strftime("%b %d %H:%M")

        }

    @database_sync_to_async
    def _delete_comment(self, data):

        comment = Comment.objects.get(id=data['comment_id'])
        comment.delete()
        return {
            'id': data['comment_id']
        }
