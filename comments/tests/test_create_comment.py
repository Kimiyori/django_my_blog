from django.test import TransactionTestCase


from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model


from channels.routing import URLRouter

from ..routing import websocket_urlpatterns

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.apps import apps


class TestCreateCommentBase(object):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test", password="12test12", email="test@example.com"
        )
        self.model = apps.get_model(
            app_label=self.app_label, model_name=self.model_name
        )
        self.comment_model = apps.get_model(
            app_label="comments", model_name=f"comment{self.model_name}"
        )
        self.post = (
            self.model.objects.create(author=self.user)
            if self.model_name == "post"
            else self.model.objects.create()
        )
        self.application = URLRouter(websocket_urlpatterns)
        self.url = f"/{self.model_name}/{self.post.id}/"

    @sync_to_async
    def get_model_count(self, model):
        return model.objects.count()

    @sync_to_async
    def get_model_instance(self, model, id):
        return model.objects.get(id=id)

    async def test_connect(self):
        communicator = WebsocketCommunicator(self.application, self.url)
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_new_comment_success(self):
        communicator = WebsocketCommunicator(self.application, self.url)
        await communicator.connect()
        data = {
            "type": "new_comment",
            "content": "test comment",
            "author": self.user.id,
        }

        await communicator.send_json_to(data)
        response = await communicator.receive_json_from()
        count = await self.get_model_count(self.comment_model)
        self.assertEqual(count, 1)
        comment = await self.get_model_instance(
            self.comment_model, response["message"]["id"]
        )
        self.assertEqual(comment.content, data["content"])

    async def test_new_comment_with_parent(self):
        communicator = WebsocketCommunicator(self.application, self.url)
        await communicator.connect()

        data1 = {
            "type": "new_comment",
            "content": "comment_1",
            "author": self.user.id,
        }
        await communicator.send_json_to(data1)
        response_parent = await communicator.receive_json_from()
        data2 = {
            "type": "new_comment",
            "content": "comment_2",
            "author": self.user.id,
            "parent": response_parent["message"]["id"],
        }
        await communicator.send_json_to(data2)
        response = await communicator.receive_json_from()

        count = await self.get_model_count(self.comment_model)
        self.assertEqual(count, 2)
        comment = await self.get_model_instance(
            self.comment_model, response["message"]["id"]
        )
        self.assertEqual(comment.content, data2["content"])
        self.assertEqual(
            response["message"]["parent"], str(response_parent["message"]["id"])
        )

    async def test_new_comment_wrong_parent(self):
        communicator = WebsocketCommunicator(self.application, self.url)
        await communicator.connect()

        data1 = {
            "type": "new_comment",
            "content": "comment_1",
            "author": self.user.id,
        }
        await communicator.send_json_to(data1)
        response_parent = await communicator.receive_json_from()
        data2 = {
            "type": "new_comment",
            "content": "comment_2",
            "author": self.user.id,
            "parent": 1234341231,
        }
        with self.assertRaises(ObjectDoesNotExist, msg="wrong parent"):
            await communicator.send_json_to(data2)
            await communicator.receive_json_from()

    async def test_new_comment_wrong_type(self):
        communicator = WebsocketCommunicator(self.application, self.url)
        await communicator.connect()
        data = {
            "type": "wrong type",
            "content": "test comment",
            "author": self.user.id,
        }
        with self.assertRaises(ValueError, msg="wrong type"):
            await communicator.send_json_to(data)
            await communicator.receive_json_from()

    async def test_new_comment_wrong_author(self):
        communicator = WebsocketCommunicator(self.application, self.url)
        await communicator.connect()
        data = {
            "type": "new_comment",
            "content": "test comment",
            "author": 354353453453,
        }
        with self.assertRaises(ObjectDoesNotExist, msg="wrong user"):
            await communicator.send_json_to(data)
            await communicator.receive_json_from()

    async def test_new_comment_empty_content(self):
        communicator = WebsocketCommunicator(self.application, self.url)
        await communicator.connect()
        data = {
            "type": "new_comment",
            "content": None,
            "author": self.user.id,
        }
        with self.assertRaises(IntegrityError, msg="empty content"):
            await communicator.send_json_to(data)
            await communicator.receive_json_from()


class TestCreateCommentPost(TestCreateCommentBase, TransactionTestCase):
    def setUp(self) -> None:
        self.model_name = "post"
        self.app_label = "post"
        super().setUp()


class TestCreateCommentManga(TestCreateCommentBase, TransactionTestCase):
    def setUp(self) -> None:
        self.model_name = "manga"
        self.app_label = "titles"
        super().setUp()


class TestCreateCommentAnime(TestCreateCommentBase, TransactionTestCase):
    def setUp(self) -> None:
        self.model_name = "anime"
        self.app_label = "titles"
        super().setUp()
