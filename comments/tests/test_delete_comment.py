
from django.test import TransactionTestCase


from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model


from channels.routing import  URLRouter

from ..routing import websocket_urlpatterns

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps

class TestDeleteCommentBase(object):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test', password='12test12', email='test@example.com')
        self.model=apps.get_model(app_label=self.app_label,
                        model_name=self.model_name)
        self.comment_model=apps.get_model(app_label='comments',
                        model_name=f'comment{self.model_name}')
        self.post = self.model.objects.create(author=self.user) if self.model_name=='post' else self.model.objects.create()
        self.application = URLRouter(websocket_urlpatterns)
        self.url=f"/{self.model_name}/{self.post.id}/"

    @sync_to_async
    def get_model_count(self, model):
        return model.objects.count()

    @sync_to_async
    def get_model_instance(self, model, id):
        return model.objects.get(id=id)

    async def test_connect(self):
        communicator = WebsocketCommunicator(
            self.application, self.url)
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_delete_comment_success(self):
        communicator = WebsocketCommunicator(
            self.application, self.url)
        await communicator.connect()
        data_create = {'type': 'new_comment',
                'content': 'test comment',
                'author': self.user.id,
                }

        await communicator.send_json_to(data_create)
        created_comment = await communicator.receive_json_from()
        count = await self.get_model_count(self.comment_model)
        self.assertEqual(count, 1)
        data_delete={
            'type':'delete_comment',
            'comment_id':created_comment['message']['id']
                }
        await communicator.send_json_to(data_delete)
        delete_comment = await communicator.receive_json_from()
        self.assertEqual(delete_comment['message']['id'],created_comment['message']['id'])
        count = await self.get_model_count(self.comment_model)
        self.assertEqual(count, 0)


    async def test_delete_comment_wrong_comment_id(self):
        communicator = WebsocketCommunicator(
            self.application, self.url)
        await communicator.connect()
        data_create = {'type': 'new_comment',
                'content': 'test comment',
                'author': self.user.id,
                }

        await communicator.send_json_to(data_create)
        await communicator.receive_json_from()
        data_delete={
            'type':'delete_comment',
            'comment_id':24242342
                }
        with self.assertRaises(ObjectDoesNotExist, msg='wrong comment id'):
            await communicator.send_json_to(data_delete)
            await communicator.receive_json_from()

    

class TestDeleteCommentPost(TestDeleteCommentBase,TransactionTestCase):
    
    def setUp(self) -> None:
        self.model_name='post'
        self.app_label='post'
        super().setUp()


class TestDeleteCommentManga(TestDeleteCommentBase,TransactionTestCase):
    
    def setUp(self) -> None:
        self.model_name='manga'
        self.app_label='titles'
        super().setUp()



class TestDeleteCommentAnime(TestDeleteCommentBase,TransactionTestCase):
    
    def setUp(self) -> None:
        self.model_name='anime'
        self.app_label='titles'
        super().setUp()