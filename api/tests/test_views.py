from api.serializers import AnimeSerializer, MangaSerializer
from post.models import Post
from rest_framework.test import APITestCase
from titles.models import Title
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.apps import apps
from rest_framework import status
from django.apps import apps




class TestTitleBase(object):

    def setUp(self):
        self.title = Title.objects.create(
            original_name='Tetsugaka Letra', russian_name='первый тест', english_name='first test')
        self.obj = self.model.objects.create(
            title=self.title, description='test_description')
        self.uri = reverse(f'{self.model_name}-list')
        self.uri_id = self.uri + f'{self.obj.id}/'
        self.user = get_user_model().objects.create_user(
            username='foo', password='bar', email='test@mail.ru')

    def test_list(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_instance(self):
        response = self.client.get(self.uri_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json().keys()) > 2)

    def test_instance_fields(self):
        response = self.client.get(self.uri_id+'?fields=title,description')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().keys()), 2)

    def test_serializer_instance(self):
        serializer_data = self.serializer(self.obj).data
        response = self.client.get(self.uri_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_post_success(self):
        data = {
            "title": {
                "original_name": "test1",
                "english_name": "test2",
                "russian_name": "test3"
            },
            "genre": [
                "Comedy",
            ],
            "theme": [
                "School",
                "Cooking"
            ],
            "image": {},
            "description": "test desc"
        }
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + str(self.user.auth_token))
        response = self.client.post(self.uri, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.model.objects.get(id=response.json()['id']))

    def test_post_not_auth(self):
        data = {
            "title": {
                "original_name": "test1",
                "english_name": "test2",
                "russian_name": "test3"
            },
            "genre": [
                "Comedy",
            ],
            "theme": [
                "School",
                "Cooking"
            ],
            "image": {},
            "description": "test desc"
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + str(self.user.auth_token))
        response = self.client.post(self.uri, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put(self):
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        data = {
            "title": {
                "original_name": "test_put",

            },

            "description": "Cultural subject explain major"
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + str(self.user.auth_token))
        response = self.client.put(self.uri_id, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.obj.refresh_from_db()
        self.assertEqual(self.obj.title.original_name, 'test_put')

    def test_patch(self):
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        data = {
            "title": {
                "original_name": "test_patch",

            },
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + str(self.user.auth_token))
        response = self.client.patch(self.uri_id, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.obj.refresh_from_db()
        self.assertEqual(self.obj.title.original_name, 'test_patch')

    def test_delete(self):
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        self.assertEqual(self.model.objects.count(), 1)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + str(self.user.auth_token))
        response = self.client.delete(self.uri_id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.model.objects.count(), 0)


class TestAnime(TestTitleBase, APITestCase):
    fixtures = ['titles/fixtures/fixtures_animetype.yaml', 'titles/fixtures/fixtures_genre.yaml',
                'titles/fixtures/fixtures_studio.yaml', 'titles/fixtures/fixtures_theme.yaml', ]

    def setUp(self):
        self.model_name = 'anime'
        self.model = apps.get_model(
            app_label='titles', model_name=self.model_name)
        self.serializer = AnimeSerializer
        super().setUp()


class TestManga(TestTitleBase, APITestCase):
    fixtures = ['titles/fixtures/fixtures_mangatype.yaml', 'titles/fixtures/fixtures_genre.yaml',
                'titles/fixtures/fixtures_magazine.yaml', 'titles/fixtures/fixtures_theme.yaml',
                'titles/fixtures/fixtures_publisher.yaml', 'titles/fixtures/fixtures_demographic.yaml', ]

    def setUp(self):
        self.model_name = 'manga'
        self.model = apps.get_model(
            app_label='titles', model_name=self.model_name)
        self.serializer = MangaSerializer
        super().setUp()


class TestBasicItems(object):

    def setUp(self):
        self.url = reverse(self.url_name)
        self.user = get_user_model().objects.create_user(
            username='foo', password='bar', email='test@mail.ru')
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + str(self.user.auth_token))

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post(self):
        response = self.client.post(self.url, data={'name': 'tt'})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class TestTheme(TestBasicItems, APITestCase):
    fixtures = ['titles/fixtures/fixtures_theme.yaml']

    def setUp(self):
        self.url_name = 'api_themes'
        super().setUp()


class TestGenre(TestBasicItems, APITestCase):
    fixtures = ['titles/fixtures/fixtures_genre.yaml']

    def setUp(self):
        self.url_name = 'api_genres'
        super().setUp()


class TestPublisher(TestBasicItems, APITestCase):
    fixtures = ['titles/fixtures/fixtures_publisher.yaml']

    def setUp(self):
        self.url_name = 'api_publishers'
        super().setUp()


class TestDemographic(TestBasicItems, APITestCase):
    fixtures = ['titles/fixtures/fixtures_demographic.yaml']

    def setUp(self):
        self.url_name = 'api_demographics'
        super().setUp()


class TestMagazine(TestBasicItems, APITestCase):
    fixtures = ['titles/fixtures/fixtures_magazine.yaml']

    def setUp(self):
        self.url_name = 'api_magazines'
        super().setUp()



class TestPost(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='foo', password='bar', email='test@mail.ru')
        self.post = Post.objects.create(author=self.user)
        self.uri = reverse(f'post-list')
        self.uri_id = self.uri + f'{self.post.id}/'

    def test_list(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Post.objects.count())

    def test_instance(self):
        response = self.client.get(self.uri_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.post.id))
    def test_instance_fields(self):
        response = self.client.get(self.uri_id+'?fields=id,title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().keys()), 2)
    
