from io import BytesIO
from django.test import TestCase
from .models import *
from .views import PostList
from django.urls import reverse, resolve
from django.test import override_settings
from PIL import Image as ImageTest
import tempfile
import datetime
from django.contrib.auth import get_user_model
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import File as FileImg
# Create your tests here.


class PostListTests(TestCase):
    def setUp(self):
        url = reverse('post_list')
        self.response = self.client.get(url)

    def test_anime_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_anime_template(self):  # new
        self.assertTemplateUsed(self.response, 'post/list.html')

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, 'Blog')

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(
            self.response, 'Hi there! I should not be on the page.')

    def test_homepage_url_resolves_homepageview(self):  # new
        view = resolve('/blog/')
        self.assertEqual(
            view.func.__name__,
            PostList.as_view().__name__
        )


def get_temporary_image(name='test', height=1000, weight=1000):
    temp_file = BytesIO()
    size = (weight, height)
    color = (255, 0, 0, 0)
    image = ImageTest.new("RGBA", size, color)
    image.save(temp_file, 'png')
    temp_file.seek(0)
    return SimpleUploadedFile(f"{name}.jpg", temp_file.getvalue())


class PostTests(TestCase):

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
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

        self.assertEqual(self.content_text.order, 1)
        self.assertEqual(self.content_file.order, 2)
        self.assertEqual(self.content_image.order, 3)
        self.assertEqual(self.content_video.order, 4)
        self.content_file1 = Content.objects.create(
            post=self.post, item=self.file_obj, order=3)
        self.content_text.refresh_from_db()
        self.content_file.refresh_from_db()
        self.content_image.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(self.content_text.order, 1)
        self.assertEqual(self.content_file.order, 2)
        self.assertEqual(self.content_file1.order, 3)
        self.assertEqual(self.content_image.order, 4)
        self.assertEqual(self.content_video.order, 5)

        setattr(self.content_file, 'order', 3)
        self.content_file.save()
        self.content_text.refresh_from_db()
        self.content_file1.refresh_from_db()
        self.content_image.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(self.content_text.order, 1)
        self.assertEqual(self.content_file.order, 3)
        self.assertEqual(self.content_file1.order, 4)
        self.assertEqual(self.content_image.order, 5)
        self.assertEqual(self.content_video.order, 6)

    def test_content_delete(self):
        self.client.force_login(self.user)
        content_id = self.content_text.id
        self.assertTrue(Content.objects.filter(
            post=self.post, id=content_id).exists())
        response = self.client.post(reverse('content_delete', kwargs={
                                    'post_id': str(self.post.id), 'id': self.content_text.id}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Content.objects.filter(
            post=self.post, id=content_id).exists())

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_detail_change(self):
        self.client.force_login(self.user)
        response_get = self.client.get(
            reverse('post_detail_change', args=[self.post.pk]))
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(
            response_get, 'post/manage/content/form.html')
        data_title = {'type': 'title', 'title': 'Test post request', }
        old_title = self.post.title
        response_post_title = self.client.post(
            reverse('post_detail_change', args=[self.post.pk]), data=data_title,)
        self.assertEqual(response_post_title.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, data_title['title'])
        self.assertNotEqual(self.post.title, old_title)

        new_image = get_temporary_image('testpost', height=500, weight=500)
        data_img = {'type': 'main_image', 'main_image': new_image, }
        self.assertEqual(self.post.main_image.height, 1000)
        response_post_img = self.client.post(
            reverse('post_detail_change', args=[self.post.pk]), data=data_img)
        self.assertEqual(response_post_img.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.main_image.height, 500)
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_modules_create(self):
        self.client.force_login(self.user)
        self.assertEqual(self.content_image.order,3)
        response = self.client.post(reverse('module_content_create', kwargs={
            'post_id': self.post.pk,
            'model_name': 'text',
            'order': 2}),data={'text':'hello'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Content.objects.get(post=self.post,order=3).item.text,'hello')
        self.content_image.refresh_from_db()
        self.assertEqual(self.content_image.order,4)

        self.assertEqual(Content.objects.get(post=self.post,order=4).item.image.height,1000)
        image=get_temporary_image('text image for create url',height=456)
        response = self.client.post(reverse('module_content_create', kwargs={
            'post_id': self.post.pk,
            'model_name': 'image',
            'order': 2}),data={'image':image})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Content.objects.get(post=self.post,order=3).item.image.height,456)
        self.assertEqual(Content.objects.get(post=self.post,order=4).item.text,'hello')

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_model_update(self):
        self.client.force_login(self.user)
        self.assertEqual(self.content_text.item.text,'Some tests')
        response_text = self.client.post(reverse('module_content_update', kwargs={
            'post_id': self.post.pk,
            'model_name': 'text',
            'id': self.text_obj.id}),data={'text':'hello'})
        self.assertEqual(response_text.status_code, 200)
        self.text_obj.refresh_from_db()
        self.assertEqual(self.content_text.item.text,'hello')
        self.assertEqual(Content.objects.get(post=self.post,order=3).item.image.height,1000)

        response_image = self.client.post(reverse('module_content_update', kwargs={
            'post_id': self.post.pk,
            'model_name': 'image',
            'id': self.img_obj.id}),data={'image':get_temporary_image('text image for update url',height=789)})
        
        self.assertEqual(response_image.status_code, 200)
        self.assertEqual(Content.objects.get(post=self.post,order=3).item.image.height,789)

        self.assertEqual(Content.objects.get(post=self.post,order=4).item.video,self.video_obj.video)
        video='https://www.youtube.com/watch?v=Wz-pNcgYo0c&list=RDWz-pNcgYo0c&start_radio=1&ab_channel=Nyanperona21'
        response_video = self.client.post(reverse('module_content_update', kwargs={
            'post_id': self.post.pk,
            'model_name': 'video',
            'id': self.video_obj.id}),data={'video':video})
        self.assertEqual(response_video.status_code, 200)
        self.assertEqual(Content.objects.get(post=self.post,order=4).item.video,video)

        self.assertEqual(Content.objects.get(post=self.post,order=2).item.file,self.file_obj.file)
        new_file=SimpleUploadedFile(
            "new_test_update.txt",
            b"these are the file contents!"
                                    )
        response_file = self.client.post(reverse('module_content_update', kwargs={
            'post_id': self.post.pk,
            'model_name': 'file',
            'id': self.file_obj.id}),data={'file':new_file})
        self.assertEqual(response_file.status_code, 200)
        self.assertEqual(Content.objects.get(post=self.post,order=2).item.file.name.split("/")[-1],new_file.name)


    def test_swap_orders(self):
        self.client.force_login(self.user)
        data={str(self.content_text.id):str(self.content_image.order),
            str(self.content_image.id):str(self.content_text.order)}
        old_text_order=self.content_text.order
        old_image_order=self.content_image.order
        response = self.client.post(reverse('content_order'),
        data=data,
        content_type="application/json",
        accept= 'application/json',
        mode='cors')
        self.assertEqual(response.status_code, 200)
        self.content_text.refresh_from_db()
        self.content_image.refresh_from_db()
        self.assertEqual(self.content_text.order,old_image_order)
        self.assertEqual(self.content_image.order,old_text_order)

    def test_post_detail(self):
        response = self.client.get(reverse('post_detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.title)
        self.assertTemplateUsed(response, 'post/manage/detail.html')
