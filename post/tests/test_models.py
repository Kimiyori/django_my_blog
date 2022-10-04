from io import BytesIO
import shutil
from django.test import TestCase
from ..models import *

from django.test import override_settings
from PIL import Image as ImageTest

import datetime
from django.contrib.auth import get_user_model
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

TEST_DIR = "test_data"


def get_temporary_image(name="test", height=1000, weight=1000):
    temp_file = BytesIO()
    size = (weight, height)
    color = (255, 0, 0, 0)
    image = ImageTest.new("RGBA", size, color)
    image.save(temp_file, "png")
    temp_file.seek(0)
    return SimpleUploadedFile(f"{name}.jpg", temp_file.getvalue())


@override_settings(MEDIA_ROOT=(TEST_DIR + "/media"))
class PostModelTests(TestCase):
    def setUp(self):
        self.test_image = get_temporary_image(
            "test_img",
        )
        self.title = "Test Post"
        self.user = get_user_model().objects.create_user(
            username="test", password="12test12", email="test@example.com"
        )

        self.date = datetime.datetime(
            2022, 5, 16, 17, 53, 21, 780213, tzinfo=datetime.timezone.utc
        )
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = self.date
            self.post = Post.objects.create(
                title=self.title,
                main_image=self.test_image,
                author=self.user,
                publish=self.date,
                created=self.date,
                updated=self.date,
                status=Post.DRAFT,
            )
            self.post2 = Post.objects.create(
                title=121212,
                main_image=self.test_image,
                author=self.user,
                publish=self.date,
                created=self.date,
                updated=self.date,
                status=Post.PUBLISHED,
            )
        self.text_obj = Text.objects.create(post=self.post, text="Some tests")
        self.file_obj = File.objects.create(
            post=self.post,
            file=SimpleUploadedFile(
                "best_file_eva.txt",
                # note the b in front of the string [bytes]
                b"these are the file contents!",
            ),
        )
        self.img_obj = Image.objects.create(post=self.post, image=self.test_image)
        self.video_obj = Video.objects.create(
            post=self.post, video="https://youtu.be/xahEdP2eJs4?list=RDxahEdP2eJs4"
        )

        self.content_text = Content.objects.create(post=self.post, item=self.text_obj)
        self.content_file = Content.objects.create(
            post=self.post, item=self.file_obj, order=2
        )
        self.content_image = Content.objects.create(
            post=self.post, item=self.img_obj, order=3
        )
        self.content_video = Content.objects.create(
            post=self.post, item=self.video_obj, order=4
        )

    def test_post_listing(self):
        self.assertEqual(self.post.title, self.title)
        self.assertEqual(self.post.author, self.user)
        self.assertIsNotNone(self.post.main_image)
        self.assertEqual(self.post.publish, self.date)
        self.assertEqual(self.post.created, self.date)
        self.assertEqual(self.post.updated, self.date)
        self.assertEqual(self.post.status, Post.DRAFT)
        self.assertEqual(self.post.contents.count(), 4)

    def test_post_content(self):
        self.assertEqual(self.content_text.item, self.text_obj)
        self.assertEqual(self.content_file.item, self.file_obj)
        self.assertEqual(self.content_image.item, self.img_obj)
        self.assertEqual(self.content_video.item, self.video_obj)

    def test_content_order(self):
        self.assertEqual(self.content_text.order, 1)
        self.assertEqual(self.content_file.order, 2)
        self.assertEqual(self.content_image.order, 3)
        self.assertEqual(self.content_video.order, 4)

    def test_wrong_type_order(self):
        with self.assertRaises(TypeError, msg="test with order as string"):
            Content.objects.create(
                post=self.post, item=self.text_obj, order="something wrong"
            )

    def test_add_new_content_with_order_first(self):
        self.content_file1 = Content.objects.create(
            post=self.post, item=self.file_obj, order=1
        )
        self.content_text.refresh_from_db()
        self.content_file.refresh_from_db()
        self.content_image.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(self.content_file1.order, 1)
        self.assertEqual(self.content_text.order, 2)
        self.assertEqual(self.content_file.order, 3)
        self.assertEqual(self.content_image.order, 4)
        self.assertEqual(self.content_video.order, 5)

    def test_add_new_content_with_order_middle(self):
        self.content_file1 = Content.objects.create(
            post=self.post, item=self.file_obj, order=3
        )
        self.content_text.refresh_from_db()
        self.content_file.refresh_from_db()
        self.content_image.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(self.content_text.order, 1)
        self.assertEqual(self.content_file.order, 2)
        self.assertEqual(self.content_file1.order, 3)
        self.assertEqual(self.content_image.order, 4)
        self.assertEqual(self.content_video.order, 5)

    def test_add_new_content_with_order_last(self):
        self.content_file1 = Content.objects.create(
            post=self.post, item=self.file_obj, order=5
        )
        self.content_text.refresh_from_db()
        self.content_file.refresh_from_db()
        self.content_image.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(self.content_text.order, 1)
        self.assertEqual(self.content_file.order, 2)
        self.assertEqual(self.content_image.order, 3)
        self.assertEqual(self.content_video.order, 4)
        self.assertEqual(self.content_file1.order, 5)

    def test_add_new_content_without_order_last(self):
        self.content_file1 = Content.objects.create(post=self.post, item=self.file_obj)
        self.content_text.refresh_from_db()
        self.content_file.refresh_from_db()
        self.content_image.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(self.content_text.order, 1)
        self.assertEqual(self.content_file.order, 2)
        self.assertEqual(self.content_image.order, 3)
        self.assertEqual(self.content_video.order, 4)
        self.assertEqual(self.content_file1.order, 5)

    def test_update_order(self):
        setattr(self.content_file, "order", 3)
        self.content_file.save()
        self.content_text.refresh_from_db()
        self.content_image.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(self.content_text.order, 1)
        self.assertEqual(self.content_file.order, 3)
        self.assertEqual(self.content_image.order, 4)
        self.assertEqual(self.content_video.order, 5)

    def test_delete_content_first(self):
        self.assertEqual(Content.objects.count(), 4)
        self.content_text.delete()
        self.content_file.refresh_from_db()
        self.content_image.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(Content.objects.count(), 3)
        self.assertEqual(self.content_file.order, 1)
        self.assertEqual(self.content_image.order, 2)
        self.assertEqual(self.content_video.order, 3)

    def test_delete_content_middle(self):
        self.assertEqual(Content.objects.count(), 4)
        self.content_image.delete()
        self.content_file.refresh_from_db()
        self.content_text.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(Content.objects.count(), 3)
        self.assertEqual(self.content_text.order, 1)
        self.assertEqual(self.content_file.order, 2)
        self.assertEqual(self.content_video.order, 3)

    def test_delete_content_last(self):
        self.assertEqual(Content.objects.count(), 4)
        self.content_video.delete()
        self.content_file.refresh_from_db()
        self.content_text.refresh_from_db()
        self.content_image.refresh_from_db()
        self.assertEqual(Content.objects.count(), 3)
        self.assertEqual(self.content_text.order, 1)
        self.assertEqual(self.content_file.order, 2)
        self.assertEqual(self.content_image.order, 3)

    def test_published_manager(self):
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Post.published.count(), 1)

    def test_post_str(self):
        self.assertEqual(str(self.post), self.title)
        self.assertEqual(str(self.post2), "121212")

    def test_content_str(self):
        self.assertEqual(
            str(self.content_text),
            f"{self.content_text.post} {self.content_text.order}",
        )

    def test_item_str(self):
        self.assertEqual(
            str(self.text_obj),
            f"{self.text_obj.__class__.__name__} from {self.text_obj.post}",
        )

    def test_item_get_model_name(self):
        self.assertEqual(
            str(self.text_obj.get_model_name()), f"{self.text_obj._meta.model_name}"
        )

    def tearDown(self):
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            print("Fail to delete test folder")
            pass
