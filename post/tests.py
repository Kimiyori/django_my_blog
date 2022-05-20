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
from django.utils import timezone
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
    def test_anime_template(self): # new
        self.assertTemplateUsed(self.response, 'post/list.html')
    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, 'Blog')
    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.')
    def test_homepage_url_resolves_homepageview(self): # new
        view = resolve('/blog/')
        self.assertEqual(
        view.func.__name__,
    PostList.as_view().__name__
        )


def get_temporary_image():
    temp_file= BytesIO()
    size = (1000, 1000)
    color = (255, 0, 0, 0)
    image = ImageTest.new("RGBA", size, color)
    image.save(temp_file, 'png')
    temp_file.seek(0)
    return FileImg(temp_file,name='image')
class MangaTests(TestCase):


    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def setUp(self):
        self.test_image = get_temporary_image()
        self.title='Test Post'
        self.user = get_user_model().objects.create_user(username='test', password='12test12', email='test@example.com')
        self.date=datetime.datetime(2022, 5, 16, 17, 53, 21, 780213, tzinfo=datetime.timezone.utc)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = self.date
            self.post=Post.objects.create(
                title=self.title,
                main_image=self.test_image.name,
                author=self.user,
                publish=self.date,
                created=self.date,
                updated=self.date,
                status=Post.DRAFT,
            )
        
        self.text_obj=Text.objects.create(post=self.post,text='Some tests')
        self.file_obj=File.objects.create(post=self.post,file=SimpleUploadedFile(
                                            "best_file_eva.txt",
                                            b"these are the file contents!"   # note the b in front of the string [bytes]
                                                                        ))
        self.img_obj=Image.objects.create(post=self.post,image=self.test_image)
        self.video_obj=Video.objects.create(post=self.post,video='https://youtu.be/xahEdP2eJs4?list=RDxahEdP2eJs4')


        self.content_text=Content.objects.create(post=self.post,item=self.text_obj,order=1)
        self.content_file=Content.objects.create(post=self.post,item=self.file_obj,order=2)
        self.content_image=Content.objects.create(post=self.post,item=self.img_obj,order=3)
        self.content_video=Content.objects.create(post=self.post,item=self.video_obj,order=4)
    def test_post_listing(self):
        self.assertEqual(self.post.title, self.title)
        self.assertEqual(self.post.author, self.user)
        self.assertIsNotNone(self.post.main_image)
        self.assertEqual(self.post.publish, self.date)
        self.assertEqual(self.post.created, self.date)
        self.assertEqual(self.post.updated, self.date)
        self.assertEqual(self.post.status, Post.DRAFT)
        self.assertEqual(self.post.contents.count(),4)

        self.assertEqual(self.content_text.item,self.text_obj)
        self.assertEqual(self.content_file.item,self.file_obj)
        self.assertEqual(self.content_image.item,self.img_obj)
        self.assertEqual(self.content_video.item,self.video_obj)

        self.assertEqual(self.content_text.order,1)
        self.assertEqual(self.content_file.order,2)
        self.assertEqual(self.content_image.order,3)
        self.assertEqual(self.content_video.order,4)
        self.content_file1=Content.objects.create(post=self.post,item=self.file_obj,order=3)
        self.content_text.refresh_from_db()
        self.content_file.refresh_from_db()
        self.content_image.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(self.content_text.order,1)
        self.assertEqual(self.content_file.order,2)
        self.assertEqual(self.content_file1.order,3)
        self.assertEqual(self.content_image.order,4)
        self.assertEqual(self.content_video.order,5)

        setattr(self.content_file,'order',3)
        self.content_file.save()
        self.content_text.refresh_from_db()
        self.content_file1.refresh_from_db()
        self.content_image.refresh_from_db()
        self.content_video.refresh_from_db()
        self.assertEqual(self.content_text.order,1)
        self.assertEqual(self.content_file.order,3)
        self.assertEqual(self.content_file1.order,4)
        self.assertEqual(self.content_image.order,5)
        self.assertEqual(self.content_video.order,6)
        
    

    def test_post_detail(self):
        response = self.client.get(reverse('post_detail', args=[self.post.pk]))
        no_response = self.client.get('/blog/12345/')
        self.assertEqual(no_response.status_code, 404)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.title)
        self.assertTemplateUsed(response, 'post/manage/detail.html')
