from io import BytesIO
from api.serializers import AnimeSerializer, AuthorsSerializer, MangaSerializer, PostSerializer, TitleSerializer
from rest_framework.test import APITestCase
from titles.models import  AuthorTable, Authors,Title
import shutil
from django.test import override_settings
from titles.tests.test_models import get_temporary_image
from PIL import Image as ImageFile
from django.apps import apps
from tempfile import NamedTemporaryFile
from django.core.files.uploadedfile import InMemoryUploadedFile

TEST_DIR = 'test_data'


class TestTitle(APITestCase):
    def setUp(self):
        self.serializer_data = {
            'original_name': 'test1',
            'english_name': 'test2',
            'russian_name': 'test3'
        }

    def test_valid_serializer(self):
        serializer = TitleSerializer(data=self.serializer_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, self.serializer_data)
        self.assertEqual(serializer.data, self.serializer_data)

    def test_partial_serializer(self):
        serializer_data = {
            'original_name': 'test1',
        }
        output_data = {
            'original_name': 'test1',
            'english_name': None,
            'russian_name': None
        }
        serializer = TitleSerializer(data=serializer_data,)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, serializer_data)
        self.assertEqual(serializer.data, output_data)

    def test_empty_serializer(self):
        serializer_data = {
        }
        serializer = TitleSerializer(data=serializer_data,)
        self.assertTrue(serializer.is_valid())

    def test_create_full_serializer(self):
        serializer = TitleSerializer(data=self.serializer_data)
        self.assertTrue(serializer.is_valid())
        created = serializer.save()
        self.assertEqual(created.original_name,
                         self.serializer_data['original_name'])
        self.assertEqual(Title.objects.count(), 1)

    def test_create_partial_serializer(self):
        serializer_data = {
            'original_name': 'test1',
        }
        serializer = TitleSerializer(data=serializer_data)
        self.assertTrue(serializer.is_valid())
        created = serializer.save()
        self.assertEqual(created.original_name,
                         serializer_data['original_name'])
        self.assertEqual(created.english_name, None)
        self.assertEqual(Title.objects.count(), 1)

    def test_update_serializer(self):

        serializer = TitleSerializer(data=self.serializer_data)
        self.assertTrue(serializer.is_valid())
        obj = serializer.save()
        self.assertEqual(obj.original_name,
                         self.serializer_data['original_name'])
        updates = serializer.update(instance=obj, validated_data={
                                    'original_name': 'test_updated'})
        self.assertEqual(updates.original_name, 'test_updated')
        self.assertEqual(Title.objects.count(), 1)


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class TestAuthors(APITestCase):

    def setUp(self):

        self.author_data = {
            'name': 'test1',
            'photo': get_temporary_image()
        }
        self.artist_data = {
            'name': 'test1',
            'photo': get_temporary_image()
        }
        self.author = AuthorTable.objects.create(**self.author_data)
        self.artist = AuthorTable.objects.create(**self.author_data)

        self.authors = Authors.objects.create(
            author=self.author, artist=self.artist)

    def test_valid_serializer(self):
        data = {'author': {'name': 'test2'}, 'artist': {'name': 'test2'}}
        serializer = AuthorsSerializer(instance=self.authors)

        self.assertEqual(serializer.data['author']['name'], 'test1')
        serializer.update(instance=self.authors, validated_data=data)
        self.authors.refresh_from_db()
        self.assertEqual(self.authors.author.name, 'test2')
        self.assertEqual(self.authors.artist.name, 'test2')

    def tearDown(self):
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            print('Fail to delete test folder')
            pass


class TestTitlesSerializator:

    def test_valid_data(self):
        serializer = self.serializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(set(serializer.validated_data), self.data.keys())

    def test_wrong_data(self):
        self.data['type'] = 'Wrong Type'
        serializer = self.serializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(serializer.errors)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_create(self):

        image = ImageFile.new("RGB", (100, 100))
        with NamedTemporaryFile(suffix=".png", mode="w+b") as tmp_file:
            image.save(tmp_file, format="png")
            tmp_file.seek(0)
            byio = BytesIO(tmp_file.read())
            inm_file = InMemoryUploadedFile(
                file=byio,
                field_name="avatar",
                name="testImage.png",
                content_type="image/png",
                size=byio.getbuffer().nbytes,
                charset=None,
            )
        self.data['image'] = {'image': inm_file}
        serializer = self.serializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        model = serializer.save()
        self.assertEqual(self.model.objects.count(), 1)
        self.assertEqual(
            list(model.genre.all().values_list('name', flat=True)), ['Comedy'])
        self.assertEqual(model.title.original_name,
                         self.data['title']['original_name'])
        self.assertEqual(model.title.english_name,
                         self.data['title']['english_name'])

    def test_update(self):

        serializer = self.serializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        model = serializer.save()
        update_serializer = self.serializer(instance=model, data={'title': {
                                            'english_name': 'test_update'},
            'genre': ['Drama'],
            'theme': ['Monsters']})
        self.assertTrue(update_serializer.is_valid())
        model = update_serializer.save()
        self.assertEqual(list(model.genre.all().values_list(
            'name', flat=True)), ['Comedy', 'Drama'])
        self.assertEqual(list(model.theme.all().values_list('name', flat=True)), [
                         'Cooking', 'Monsters', 'School'])
        self.assertEqual(model.title.original_name,
                         self.data['title']['original_name'])
        self.assertEqual(model.title.english_name, 'test_update')

    def tearDown(self):
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass


class TestAnime(TestTitlesSerializator, APITestCase):
    fixtures = ['titles/fixtures/fixtures_animetype.yaml', 'titles/fixtures/fixtures_genre.yaml',
                'titles/fixtures/fixtures_studio.yaml', 'titles/fixtures/fixtures_theme.yaml', ]

    def setUp(self):
        self.model = apps.get_model(app_label='titles', model_name='anime')
        self.serializer = AnimeSerializer
        self.data = {
            "title": {
                "original_name": "test1",
                "english_name": "test2",
                "russian_name": "test3"
            },
            "type": "TV Show",
            "studio": [
                "Kyoto Animation"
            ],
            "premiere": "2022-08-15",
            "episodes": 2147483647,
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


class TestManga(TestTitlesSerializator, APITestCase):
    fixtures = ['titles/fixtures/fixtures_mangatype.yaml', 'titles/fixtures/fixtures_genre.yaml',
                'titles/fixtures/fixtures_magazine.yaml', 'titles/fixtures/fixtures_theme.yaml',
                'titles/fixtures/fixtures_publisher.yaml', 'titles/fixtures/fixtures_demographic.yaml', ]

    def setUp(self):
        self.model = apps.get_model(app_label='titles', model_name='manga')
        self.serializer = MangaSerializer
        self.data = {
            "title": {
                "original_name": "test1",
                "english_name": "test2",
                "russian_name": "test3"
            },
            "premiere": "2022-08-15",
            "volumes": 12,
            "chapters": 96,
            "authors": {
                "author": {
                    "name": "string"
                },
                "artist": {
                    "name": "string"
                }
            },
            "publisher": [
                "Shueisha"
            ],
            "genre": [
                "Comedy",
            ],
            "theme": [
                "School",
                "Cooking"
            ],
            "magazine": [
                "Afternoon"
            ],
            "demographic": "Shounen",
            "type": "Manga",
            "description": "string",
        }


class TestPostSerializer(APITestCase):
    fixtures = ['post/fixtures/fixtures_post.yaml',
                'post/fixtures/fixtures_items.yaml',
                'accounts/fixtures/fixtures_users.yaml']

    def setUp(self):
        self.data = {
            "id": "df3caddd-cec6-40e7-847a-095b8bb79c9c",
            "title": "aaadqaawfwfwf",
            "author": 
            {'username':"Kimiyori"},
            "publish": "2022-07-09T14:42:21Z",
            "created": "2022-07-09T14:42:32.374538Z",
            "updated": "2022-07-09T14:42:32.374548Z",
            "status": "draft",
        }
    def test_valid(self):
        serializer=PostSerializer(data=self.data)
        serializer.is_valid()
        print(serializer.errors)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['title'],self.data['title'])
