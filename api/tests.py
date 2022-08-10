import json
from api.serializers import AnimeSerializer, MangaSerializer
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
import api.views as views
from titles.models import Anime, AnimeType, Manga, MangaType, Title
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate

class TestToken(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.title = Title.objects.create(
            original_name='Tetsugaka Letra', russian_name='первый тест', english_name='first test')
        self.anime = Anime.objects.create(title=self.title)
        self.anime_type=AnimeType.objects.create(name='TV Show')
        self.uri = 'http://127.0.0.1:8000/api/anime/'
        self.uri_id = self.uri + f'{self.anime.id}/'
        self.user = get_user_model().objects.create_user(
            username='foo', password='bar', email='test@mail.ru')
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        self.token=Token.objects.get(user=self.user)

    
    def test_token(self):
        self.assertEqual(self.user.auth_token,self.token)

    def test_post(self):
        data = {
            "title": {
                "original_name": "te1st",
                "english_name": "test2",
                "russian_name": "test3"
            },
            'type':'TV Show',
            "premiere": "2022-07-18",
            "episodes": 2147,

            "description": "Cultural subject explain major"
        }
        self.client.force_authenticate(user=self.user,token=self.user.auth_token)
        response = self.client.post(self.uri, data=data, format='json')
        self.assertEqual(response.status_code, 201,
                         'Expected Response Code 201, received {0} instead.'
                         .format(response.status_code))
        self.assertEqual(response.json()['episodes'], 2147)
    def test_post_header(self):
        data = {
            "title": {
                "original_name": "test",
                "english_name": "test2",
                "russian_name": "test3"
            },
            'type':'TV Show',
            "premiere": "2022-07-18",
            "episodes": 2147,

            "description": "Cultural subject explain major"
        }
        self.factory = APIRequestFactory()

        request = self.factory.post(self.uri ,
                HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token),
                data=data,
                format='json')
        self.view = views.AnimeList.as_view({'post': 'create'})
        response = self.view(request)

        self.assertEqual(response.status_code, 201,
                         'Expected Response Code 201, received {0} instead.'
                         .format(response.status_code))
        self.assertEqual(Anime.objects.count(),2)
    

class TestRequest(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = views.AnimeList.as_view({'get': 'list'})
        self.anime_list_uri = 'anime'
        self.title = Title.objects.create(
            original_name='Tetsugaka Letra', russian_name='первый тест', english_name='first test')
        self.anime_id = Anime.objects.create(title=self.title)
        self.view1 = views.AnimeList.as_view({'get': 'retrieve'})

    def test_list(self):
        request = self.factory.get(self.anime_list_uri)
        response = self.view(request)
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))

    def test_anime_id(self):
        request = self.factory.get(self.anime_list_uri)
        response = self.view1(request, pk=self.anime_id.id)
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))


class TestAnime(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.title = Title.objects.create(
            original_name='Tetsugaka Letra', russian_name='первый тест', english_name='first test')
        self.anime = Anime.objects.create(title=self.title)
        self.anime_type=AnimeType.objects.create(name='TV Show')
        self.uri = 'http://127.0.0.1:8000/api/anime/'
        self.uri_id = self.uri + f'{self.anime.id}/'
        self.user = get_user_model().objects.create_user(
            username='foo', password='bar', email='test@mail.ru')
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()

    # ...
    def test_list(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))


    def test_instance(self):
        response = self.client.get(self.uri_id)
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))

    def test_serializer_instance(self):
        serializer_data=AnimeSerializer(self.anime).data
        response = self.client.get(self.uri_id)
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))
        self.assertEqual(response.data,serializer_data)

    def test_post(self):
        data = {
            "title": {
                "original_name": "test",
                "english_name": "test2",
                "russian_name": "test3"
            },
            'type':'TV Show',
            "premiere": "2022-07-18",
            "episodes": 2147,

            "description": "Cultural subject explain major"
        }
        self.client.force_authenticate(user=self.user,token=self.user.auth_token)
        response = self.client.post(self.uri, data=data, format='json')
        self.assertEqual(response.status_code, 201,
                         'Expected Response Code 201, received {0} instead.'
                         .format(response.status_code))
        self.assertEqual(response.json()['episodes'], 2147)

    def test_put(self):
        data = {
            "title": {
                "original_name": "test",

            },

            "premiere": "2022-07-18",
            "episodes": 2147,

            "description": "Cultural subject explain major"
        }
        self.assertEqual(self.anime.title.original_name, 'Tetsugaka Letra')
        self.assertEqual(self.anime.episodes, None)
        self.client.force_authenticate(user=self.user,token=self.user.auth_token)
        response = self.client.put(self.uri_id, data=data, format='json')
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200 , received {0} instead.'
                         .format(response.status_code))
        self.anime.refresh_from_db()
        self.assertEqual(self.anime.title.original_name, 'test')
        self.assertEqual(self.anime.episodes, 2147)

    def test_patch(self):
        data = {
            "title": {
                "original_name": "test1",

            },

            "premiere": "2022-07-18",
            "episodes": 2147,

            "description": "Cultural subject explain major"
        }
        self.assertEqual(self.anime.title.original_name, 'Tetsugaka Letra')
        self.client.force_authenticate(user=self.user,token=self.user.auth_token)
        response = self.client.patch(self.uri_id, data=data, format='json')
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))
        self.anime.refresh_from_db()
        self.assertEqual(self.anime.title.original_name, 'test1')

    def test_delete(self):
        self.assertEqual(Anime.objects.count(), 1)
        self.client.force_authenticate(user=self.user,token=self.user.auth_token)
        response = self.client.delete(self.uri_id)
        self.assertEqual(response.status_code, 204,
                         'Expected Response Code 204, received {0} instead.'
                         .format(response.status_code))
        self.assertEqual(Anime.objects.count(), 0)


class TestManga(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.title = Title.objects.create(
            original_name='Tetsugaka Letra', russian_name='первый тест', english_name='first test')
        self.anime = Manga.objects.create(title=self.title)
        self.anime_type=MangaType.objects.create(name='Manga')
        self.uri = 'http://127.0.0.1:8000/api/manga/'
        self.uri_id = self.uri + f'{self.anime.id}/'
        self.user = get_user_model().objects.create_user(
            username='foo', password='bar', email='test@mail.ru')
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()

    # ...
    def test_list(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))


    def test_instance(self):
        response = self.client.get(self.uri_id)
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))

    def test_serializer_instance(self):
        serializer_data=MangaSerializer(self.anime).data
        response = self.client.get(self.uri_id)
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))
        self.assertEqual(response.data,serializer_data)

    def test_post(self):
        data = {
            "title": {
                "original_name": "test",
                "english_name": "test2",
                "russian_name": "test3"
            },
            'type':'Manga',
            "premiere": "2022-07-18",
            "chapters": 2147,

            "description": "Cultural subject explain major"
        }

        self.client.force_authenticate(user=self.user,token=self.user.auth_token)
        response = self.client.post(self.uri, data=data, format='json')
        self.assertEqual(response.status_code, 201,
                         'Expected Response Code 201, received {0} instead.'
                         .format(response.status_code))
        self.assertEqual(response.json()['chapters'], 2147)

    def test_put(self):
        data = {
            "title": {
                "original_name": "test",

            },

            "premiere": "2022-07-18",
            "chapters": 2147,

            "description": "Cultural subject explain major"
        }
        self.assertEqual(self.anime.title.original_name, 'Tetsugaka Letra')
        self.assertEqual(self.anime.chapters, None)
        self.client.force_authenticate(user=self.user,token=self.user.auth_token)
        response = self.client.put(self.uri_id, data=data, format='json')
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200 , received {0} instead.'
                         .format(response.status_code))
        self.anime.refresh_from_db()
        self.assertEqual(self.anime.title.original_name, 'test')
        self.assertEqual(self.anime.chapters, 2147)

    def test_patch(self):
        data = {
            "title": {
                "original_name": "test1",

            },

            "premiere": "2022-07-18",
            "chapters": 2147,

            "description": "Cultural subject explain major"
        }
        self.assertEqual(self.anime.title.original_name, 'Tetsugaka Letra')
        self.client.force_authenticate(user=self.user,token=self.user.auth_token)
        response = self.client.patch(self.uri_id, data=data, format='json')
        self.assertEqual(response.status_code, 200,
                         'Expected Response Code 200, received {0} instead.'
                         .format(response.status_code))
        self.anime.refresh_from_db()
        self.assertEqual(self.anime.title.original_name, 'test1')

    def test_delete(self):
        self.assertEqual(Manga.objects.count(), 1)
        self.client.force_authenticate(user=self.user,token=self.user.auth_token)
        response = self.client.delete(self.uri_id)
        self.assertEqual(response.status_code, 204,
                         'Expected Response Code 204, received {0} instead.'
                         .format(response.status_code))
        self.assertEqual(Manga.objects.count(), 0)
