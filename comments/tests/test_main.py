from sqlite3 import connect
from django.test import SimpleTestCase, TestCase, TransactionTestCase

from ..models import CommentPost
from channels.db import database_sync_to_async
from ..consumers import PostCommentsConsumer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from post.models import Post
from channels.db import database_sync_to_async
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path, path
from ..routing import websocket_urlpatterns
import json
from channels.testing import ChannelsLiveServerTestCase
from channels.auth import login
from asgiref.sync import sync_to_async, async_to_sync
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

class Tests(TransactionTestCase):
    #databases = '__all__'

    def setUp(self):
        self.title = 'Test Post'
        self.user = get_user_model().objects.create_user(
            username='test', password='12test12', email='test@example.com')
        self.post = Post.objects.create(
            title=self.title,
            author=self.user,
        )
        self.application = URLRouter(websocket_urlpatterns)

    @sync_to_async
    def get_model_count(self, model):
        return model.objects.count()

    @sync_to_async
    def get_model_instance(self, model, id):
        return model.objects.get(id=id)

    async def test_connect(self):
        communicator = WebsocketCommunicator(
            self.application, f"/post/{self.post.id}/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_new_comment_success(self):
        communicator = WebsocketCommunicator(
            self.application, f"/post/{self.post.id}/")
        await communicator.connect()
        data = {'type': 'new_comment',
                'content': 'test comment',
                'author': self.user.id,
                }

        await communicator.send_json_to(data)
        response = await communicator.receive_json_from()
        count = await self.get_model_count(CommentPost)
        self.assertEqual(count, 1)
        comment = await self.get_model_instance(CommentPost, response['message']['id'])
        self.assertEqual(comment.content, data['content'])

    async def test_new_comment_with_parent(self):
        communicator = WebsocketCommunicator(
            self.application, f"/post/{self.post.id}/")
        await communicator.connect()

        data1 = {'type': 'new_comment',
                'content': 'comment_1',
                'author': self.user.id,
                }
        await communicator.send_json_to(data1)
        response_parent= await communicator.receive_json_from()
        data2 = {'type': 'new_comment',
                'content': 'comment_2',
                'author': self.user.id,
                'parent':response_parent['message']['id']
                }
        await communicator.send_json_to(data2)
        response = await communicator.receive_json_from()

        count = await self.get_model_count(CommentPost)
        self.assertEqual(count, 2)
        comment = await self.get_model_instance(CommentPost, response['message']['id'])
        self.assertEqual(comment.content, data2['content'])
        self.assertEqual(response['message']['parent'], str(response_parent['message']['id']))
    
    async def test_new_comment_wrong_parent(self):
        communicator = WebsocketCommunicator(
            self.application, f"/post/{self.post.id}/")
        await communicator.connect()

        data1 = {'type': 'new_comment',
                'content': 'comment_1',
                'author': self.user.id,
                }
        await communicator.send_json_to(data1)
        response_parent= await communicator.receive_json_from()
        data2 = {'type': 'new_comment',
                'content': 'comment_2',
                'author': self.user.id,
                'parent':response_parent['message']['id']
                }
        await communicator.send_json_to(data2)
        response = await communicator.receive_json_from()

        count = await self.get_model_count(CommentPost)
        self.assertEqual(count, 2)
        comment = await self.get_model_instance(CommentPost, response['message']['id'])
        self.assertEqual(comment.content, data2['content'])
        self.assertEqual(response['message']['parent'], str(response_parent['message']['id']))


    async def test_new_comment_wrong_type(self):
        communicator = WebsocketCommunicator(
            self.application, f"/post/{self.post.id}/")
        await communicator.connect()
        data = {'type': 'wrong type',
                'content': 'test comment',
                'author': self.user.id,
                }
        with self.assertRaises(ValueError, msg='wrong type'):
            await communicator.send_json_to(data)
            await communicator.receive_json_from()

    async def test_new_comment_wrong_author(self):
        communicator = WebsocketCommunicator(
            self.application, f"/post/{self.post.id}/")
        await communicator.connect()
        data = {'type': 'new_comment',
                'content': 'test comment',
                'author': 354353453453,
                }
        with self.assertRaises(ObjectDoesNotExist, msg='wrong user'):
            await communicator.send_json_to(data)
            await communicator.receive_json_from()

    async def test_new_comment_empty_content(self):
        communicator = WebsocketCommunicator(
            self.application, f"/post/{self.post.id}/")
        await communicator.connect()
        data = {'type': 'new_comment',
                'content': None,
                'author': self.user.id,
                }
        with self.assertRaises(IntegrityError, msg='empty content'):
            await communicator.send_json_to(data)
            await communicator.receive_json_from()
    
