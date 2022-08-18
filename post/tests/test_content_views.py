
from embed_video.backends import YoutubeBackend
from io import BytesIO
import shutil
from uuid import uuid4
from django.test import TestCase
from ..models import *
from django.urls import reverse
from django.test import override_settings
from PIL import Image as ImageTest
import datetime
from django.contrib.auth import get_user_model
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from..forms import PostForm

# Create your tests here.

TEST_DIR = 'test_data'


def get_temporary_image(name='test', height=1000, weight=1000):
    temp_file = BytesIO()
    size = (weight, height)
    color = (255, 0, 0, 0)
    image = ImageTest.new("RGBA", size, color)
    image.save(temp_file, 'png')
    temp_file.seek(0)
    return SimpleUploadedFile(f"{name}.jpg", temp_file.getvalue())


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class PostModelTests(TestCase):

    def setUp(self):
        self.test_image = get_temporary_image('test_img',)
        self.title = 'Test Post'
        self.user = get_user_model().objects.create_user(
            username='test', password='12test12', email='test@example.com')

        self.date = datetime.datetime(
            2022, 5, 16, 17, 53, 21, 780213, tzinfo=datetime.timezone.utc)
        with mock.patch('django.utils.timezone.now') as mock_now:
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

        self.text_obj = Text.objects.create(post=self.post, text='Some tests')
        self.file_obj = File.objects.create(post=self.post, file=SimpleUploadedFile(
            "best_file_eva.txt",
            # note the b in front of the string [bytes]
                                            b"these are the file contents!"
                                            ))
        self.img_obj = Image.objects.create(
            post=self.post, image=self.test_image)
        self.video_obj = Video.objects.create(
            post=self.post, video='https://youtu.be/xahEdP2eJs4?list=RDxahEdP2eJs4')

        self.content_text = Content.objects.create(
            post=self.post, item=self.text_obj, order=1)
        self.content_file = Content.objects.create(
            post=self.post, item=self.file_obj, order=2)
        self.content_image = Content.objects.create(
            post=self.post, item=self.img_obj, order=3)
        self.content_video = Content.objects.create(
            post=self.post, item=self.video_obj, order=4)

    def test_create_post_post(self):
        self.client.force_login(self.user)
        img = image = get_temporary_image(
            'text image for create url', height=456)
        response = self.client.post(
            reverse('post_detail_create'),
            data={'title': 'test', 'main_image': img})
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(post.title, 'test')

    def test_create_post_get(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('post_detail_create'),
          )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'post/manage/content/form_create.html')

    def test_post_delete_success(self):
        self.client.force_login(self.user)
        post_id = self.post.pk
        self.assertTrue(Post.objects.filter(id=post_id).exists())
        response = self.client.post(
            reverse('post_delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(id=post_id).exists())

    def test_post_delete_fail(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('post_delete', args=[uuid4()]))
        self.assertEqual(response.status_code, 404)

    def test_post_detail_change_get(self):
        self.client.force_login(self.user)
        response_get = self.client.get(
            reverse('post_detail_change', args=[self.post.pk]))
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(
            response_get, 'post/manage/content/form.html')
        self.assertTrue(isinstance(
            response_get.context['main_form'], PostForm))
        self.assertEqual(len(response_get.context['items']), 4)
        self.assertEqual(response_get.context['object'].id, self.post.id)
        self.assertEqual(
            response_get.context['items'][0]['id'], self.content_text.id)
        self.assertEqual(
            response_get.context['items'][0]['order'], self.content_text.order)
        self.assertEqual(
            response_get.context['items'][0]['model'], self.text_obj._meta.model_name)
        self.assertEqual(
            response_get.context['items'][0]['item_id'], str(self.text_obj.id))

    def test_post_detail_change_wrong_id(self):
        self.client.force_login(self.user)
        response_get = self.client.get(
            reverse('post_detail_change', args=[uuid4()]))
        self.assertEqual(response_get.status_code, 302)

    def test_post_detail_change_wrong_user(self):
        user = get_user_model().objects.create_user(
            username='test2', password='12test12', email='test2@example.com')
        self.client.force_login(user)
        response_get = self.client.get(
            reverse('post_detail_change', args=[self.post.pk]))
        self.assertEqual(response_get.status_code, 302)

    # def test_post_detail_change_post_invalid_form(self):
    #     self.client.force_login(self.user)
    #     data_title = {'type': 'main_image', 'title': 'Test post request', }
    #     with self.assertRaises(ValidationError,msg='invalid form'):
    #         self.client.post(reverse('post_detail_change', 
    #                             args=[self.post.pk]), 
    #                             data=data_title,)

    def test_post_detail_change_post_title(self):
        self.client.force_login(self.user)
        data_title = {'type': 'title', 'title': 'Test post request', }
        response_post_title = self.client.post(
            reverse('post_detail_change', args=[self.post.pk]), data=data_title,)
        self.assertEqual(response_post_title.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, data_title['title'])

    def test_post_detail_change_post_image(self):
        self.client.force_login(self.user)
        new_image = get_temporary_image('testpost', height=500, weight=500)
        data_img = {'type': 'main_image', 'main_image': new_image, }
        self.assertEqual(self.post.main_image.height, 1000)
        response_post_img = self.client.post(
            reverse('post_detail_change', args=[self.post.pk]), data=data_img)
        self.assertEqual(response_post_img.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.main_image.height, 500)

    def test_modules_create_wrong_model_name(self):
        self.client.force_login(self.user)
        with self.assertRaises(ValidationError, msg='validation error'):
            response = self.client.post(reverse('module_content_create', kwargs={
                'post_id': self.post.pk,
                'model_name': 'video',
                'order': 2}), data={'text': 'hello'})

    def test_modules_create_text_without_order(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('module_content_create', kwargs={
            'post_id': self.post.pk,
            'model_name': 'text', }), data={'text': 'hello'})
        self.assertEqual(response.status_code, 200)
        self.content_image.refresh_from_db()
        self.assertEqual(Content.objects.get(
            post=self.post.pk, order=5).item.text, 'hello')

    def test_modules_create_text(self):
        self.client.force_login(self.user)
        self.assertEqual(self.content_image.order, 3)
        response = self.client.post(reverse('module_content_create', kwargs={
            'post_id': self.post.pk,
            'model_name': 'text',
            'order': 2}), data={'text': 'hello'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Content.objects.get(
            post=self.post, order=3).item.text, 'hello')
        self.content_image.refresh_from_db()
        self.assertEqual(self.content_image.order, 4)

    def test_modules_create_image(self):
        self.client.force_login(self.user)
        self.assertEqual(Content.objects.get(
            post=self.post, order=3).item.image.height, 1000)
        image = get_temporary_image('text image for create url', height=456)
        response = self.client.post(reverse('module_content_create', kwargs={
            'post_id': self.post.pk,
            'model_name': 'image',
            'order': 2}), data={'image': image})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Content.objects.get(
            post=self.post, order=3).item.image.height, 456)
        self.assertEqual(Content.objects.get(
            post=self.post, order=4).item.image.height, 1000)

    def test_modules_create_video_url(self):
        self.client.force_login(self.user)
        self.assertEqual(Content.objects.get(
            post=self.post, order=1).item.text, 'Some tests')
        url = 'https://www.youtube.com/watch?v=U6IPdxz24ao&list=RDU6IPdxz24ao&start_radio=1&ab_channel=EpicAnimeMusic'
        response = self.client.post(reverse('module_content_create', kwargs={
            'post_id': self.post.pk,
            'model_name': 'video',
            'order': 0}), data={'video': url})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Content.objects.get(
            post=self.post, order=2).item.text, 'Some tests')
        self.assertEqual(Content.objects.get(
            post=self.post, order=1).item.video, YoutubeBackend(url=url).get_url())

    def test_model_create_file(self):
        self.client.force_login(self.user)
        new_file = SimpleUploadedFile(
            "new_test_update.txt",
            b"these are the file contents!"
        )
        response_file = self.client.post(reverse('module_content_create', kwargs={
            'post_id': self.post.pk,
            'model_name': 'file',
            'order': 1}), data={'file': new_file})
        self.assertEqual(response_file.status_code, 200)
        self.assertEqual(Content.objects.get(
            post=self.post, order=2).item.file.name.split("/")[-1], new_file.name)
        self.content_file.refresh_from_db()
        self.assertEqual(self.content_file.order, 3)

    def test_model_update_text(self):
        self.client.force_login(self.user)
        self.assertEqual(self.content_text.item.text, 'Some tests')
        response_text = self.client.post(reverse('module_content_update', kwargs={
            'post_id': self.post.pk,
            'model_name': 'text',
            'id': self.text_obj.id}), data={'text': 'hello'})
        self.assertEqual(response_text.status_code, 200)
        self.text_obj.refresh_from_db()
        self.assertEqual(self.content_text.item.text, 'hello')

    def test_model_update_image(self):
        self.client.force_login(self.user)
        response_image = self.client.post(reverse('module_content_update', kwargs={
            'post_id': self.post.pk,
            'model_name': 'image',
            'id': self.img_obj.id}), data={
                'image': get_temporary_image('text image for update url', height=789)})
        self.assertEqual(response_image.status_code, 200)
        self.assertEqual(Content.objects.get(
            post=self.post, order=3).item.image.height, 789)

    def test_model_update_video(self):
        self.client.force_login(self.user)
        self.assertEqual(Content.objects.get(
            post=self.post, order=4).item.video,
            YoutubeBackend(url='https://youtu.be/xahEdP2eJs4?list=RDxahEdP2eJs4').get_url())
        video = 'https://www.youtube.com/watch?v=Wz-pNcgYo0c&list=RDWz-pNcgYo0c&start_radio=1&ab_channel=Nyanperona21'
        response_video = self.client.post(reverse('module_content_update', kwargs={
            'post_id': self.post.pk,
            'model_name': 'video',
            'id': self.video_obj.id}), data={'video': video})
        self.assertEqual(response_video.status_code, 200)
        self.assertEqual(Content.objects.get(
            post=self.post, order=4).item.video, YoutubeBackend(url=video).get_url())

    def test_model_update_file(self):
        self.client.force_login(self.user)
        self.assertEqual(Content.objects.get(
            post=self.post, order=2).item.file, self.file_obj.file)
        new_file = SimpleUploadedFile(
            "new_test_update.txt",
            b"these are the file contents!"
        )
        response_file = self.client.post(reverse('module_content_update', kwargs={
            'post_id': self.post.pk,
            'model_name': 'file',
            'id': self.file_obj.id}), data={'file': new_file})
        self.assertEqual(response_file.status_code, 200)
        self.assertEqual(Content.objects.get(
            post=self.post, order=2).item.file.name.split("/")[-1], new_file.name)

    def test_content_delete__success(self):
        self.client.force_login(self.user)
        content_id = self.content_text.id
        self.assertEqual(Text.objects.count(), 1)
        response = self.client.post(reverse('content_delete', kwargs={
                                    'post_id': str(self.post.id),
                                    'id': self.content_text.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Content.objects.count(), 3)
        self.assertFalse(Content.objects.filter(
            post=self.post, id=content_id).exists())
        self.assertEqual(Text.objects.count(), 0)

    def test_content_delete_fail_post_id(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('content_delete', kwargs={
                                    'post_id': str(uuid4()),
                                    'id': self.content_text.id}))
        self.assertEqual(response.status_code, 404)

    def test_content_delete_fail_content_id(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('content_delete', kwargs={
                                    'post_id': str(self.post.id),
                                    'id': 1212121}))
        self.assertEqual(response.status_code, 404)

    def test_swap_orders(self):
        self.client.force_login(self.user)
        data = {str(self.content_text.id): str(self.content_image.order),
                str(self.content_image.id): str(self.content_text.order)}
        old_text_order = self.content_text.order
        old_image_order = self.content_image.order
        response = self.client.post(reverse('content_order'),
                                    data=data,
                                    content_type="application/json",
                                    accept='application/json',
                                    mode='cors')
        self.assertEqual(response.status_code, 200)
        self.content_text.refresh_from_db()
        self.content_image.refresh_from_db()
        self.assertEqual(self.content_text.order, old_image_order)
        self.assertEqual(self.content_image.order, old_text_order)

    def tearDown(self):
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            print('Fail to delete test folder')
            pass
