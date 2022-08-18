from django.test import TransactionTestCase


from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
import redis

from channels.routing import  URLRouter

from ..routing import websocket_urlpatterns

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from post.models import Post
from django.conf import settings
class TestDeleteCommentBase(TransactionTestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test', password='12test12', email='test@example.com')
        self.post = Post.objects.create(author=self.user) 
        self.application = URLRouter(websocket_urlpatterns)
        self.url=f"/post/{self.post.id}/"


    @sync_to_async
    def get_model_instance(self, model, id):
        return model.objects.get(id=id)



    async def test_delete_comment_success(self):
        communicator = WebsocketCommunicator(
            self.application, self.url)
        await communicator.connect()
        data = {'type': 'increment_views',
                }

        await communicator.send_json_to(data)
        await communicator.receive_json_from()
        r = redis.Redis(host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        db=settings.REDIS_DB)
        self.assertEqual(int(r.get(f'post:{self.post.id}:views')),1)
        await communicator.send_json_to(data)
        await communicator.receive_json_from()
        self.assertEqual(int(r.get(f'post:{self.post.id}:views')),2)

