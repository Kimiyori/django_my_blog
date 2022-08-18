from io import BytesIO
from django.test import TestCase
from ..models import *
from django.template.defaultfilters import slugify
from django.test import override_settings
from PIL import Image as ImageTest

import datetime

from django.core.files.images import ImageFile
import shutil

# Create your tests here.

TEST_DIR = 'test_data'


def get_temporary_image():
    """Create temporary file for test"""
    temp_file = BytesIO()
    size = (1000, 1000)
    color = (255, 0, 0, 0)
    image = ImageTest.new("RGBA", size, color)
    image.save(temp_file, 'png')
    temp_file.seek(0)
    return ImageFile(temp_file, name='test')


class BaseTitleTests(object):

    def setUp(self):
        self.title = Title.objects.create(
            original_name='Tetsugaka Letra', russian_name='первый тест', english_name='first test')

        self.test_image = get_temporary_image()
        self.image = Image.objects.create(image=self.test_image)
        self.genre1 = Genre.objects.create(
            name='Romance', slug=slugify('Romance'))
        self.genre2 = Genre.objects.create(
            name='Action', slug=slugify('Action'))

        self.theme1 = Theme.objects.create(
            name='School', slug=slugify('School'))
        self.theme2 = Theme.objects.create(name='Garem', slug=slugify('Garem'))

        self.description = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eu lectus arcu. Donec sit amet orci eget sapien tempor vehicula. 
        Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Quisque vitae pellentesque nibh, nec fermentum tortor.
         Nullam bibendum felis non magna pretium dapibus. Donec ex tellus, rhoncus at volutpat non, feugiat vel mauris. Nunc eu euismod arcu, sed feugiat nibh.
          Etiam ac placerat velit, et varius velit. Cras sit amet rutrum metus. Sed nibh ex, gravida in vulputate ut, eleifend in est."""

    def tearDown(self):
        try:
            print(f'Delete test folder from {self.__class__.__name__}')
            shutil.rmtree(TEST_DIR)
        except OSError:
            print('Fail to delete test folder')
            pass


class MangaModelTests(BaseTitleTests, TestCase):


    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def setUp(self):
        super().setUp()
        self.manga_type = MangaType.objects.create(
            name='manga', slug=slugify('manga'))

        self.author = AuthorTable.objects.create(
            name='Sui Ishida', pseudonym='Sui Ishida', photo=self.test_image)
        self.artist = AuthorTable.objects.create(
            name='Ius Adihsi', pseudonym='Ius Adihsi', photo=self.test_image)
        self.authors = Authors.objects.create(
            author=self.author, artist=self.artist)

        self.publisher1 = Publisher.objects.create(
            name='Kodansha', slug=slugify('Kodansha'), image=self.test_image)
        self.publisher2 = Publisher.objects.create(
            name='Shueisha', slug=slugify('Shueisha'), image=self.test_image)

        self.magazine1 = Magazine.objects.create(
            name='Shounen Jump', slug=slugify('Shounen Jump'))
        self.magazine2 = Magazine.objects.create(
            name='Jump +', slug=slugify('Jump +'))

        self.demographic = Demographic.objects.create(
            name='Shounen', slug=slugify('Shounen'))

        self.manga = Manga.objects.create(
            title=self.title,
            type=self.manga_type,
            authors=self.authors,
            premiere=datetime.date.today(),
            volumes=12,
            chapters=96,
            image=self.image,
            demographic=self.demographic,
            description=self.description
        )
        self.manga2 = Manga.objects.create(
            type=self.manga_type,
            authors=self.authors,
            premiere=datetime.date.today(),
            volumes=12,
            chapters=96,
            demographic=self.demographic,
        )
        self.manga.publisher.set([self.publisher1.pk, self.publisher2.pk])
        self.manga.genre.set([self.genre1.pk, self.genre2.pk])
        self.manga.theme.set([self.theme1.pk, self.theme2.pk])
        self.manga.magazine.set([self.magazine1.pk, self.magazine2.pk])

    def test_manga_count_items(self):
        self.assertTrue(Manga.objects.count(), 2)

    def test_manga_listing(self):
        self.assertEqual(self.manga.title, self.title)
        self.assertEqual(self.manga.authors, self.authors)
        self.assertEqual(self.manga.type, self.manga_type)
        self.assertEqual(self.manga.premiere, datetime.date.today())
        self.assertEqual(self.manga.volumes, 12)
        self.assertEqual(self.manga.chapters, 96)
        self.assertEqual(self.manga.demographic, self.demographic)
        self.assertEqual(self.manga.publisher.count(), 2)
        self.assertEqual(self.manga.genre.count(), 2)
        self.assertEqual(self.manga.theme.count(), 2)
        self.assertEqual(self.manga.magazine.count(), 2)

    def test_string_representation(self):
        self.assertEqual(str(self.manga), str(self.title))
        self.assertEqual(str(self.manga2), 'Name does not exist')
        self.assertEqual(str(self.demographic), 'Shounen')
        self.assertEqual(str(self.publisher1), 'Kodansha')
        self.assertEqual(str(self.manga_type), 'manga')
        self.assertEqual(str(self.author), 'Sui Ishida')
        self.assertEqual(str(self.authors),
                         f'Author-{self.author} Artist-{self.artist}')
        self.assertEqual(str(self.theme1), 'School')
        self.assertEqual(str(self.magazine1), 'Shounen Jump')

    def test_get_description_success(self):
        self.assertEqual(self.manga.get_desc(), self.description)

    def test_get_description_fail(self):
        self.assertEqual(self.manga2.get_desc(), "No description")

    def test_delete(self):
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Title.objects.count(), 1)
        self.assertEqual(Authors.objects.count(), 1)
        self.manga.delete()
        self.assertEqual(Image.objects.count(), 0)
        self.assertEqual(Title.objects.count(), 0)
        self.assertEqual(Authors.objects.count(), 0)


class AnimeModelTests(BaseTitleTests, TestCase):

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def setUp(self):
        super().setUp()

        self.studio1 = Studio.objects.create(
            name='KyoAni', slug=slugify('KyoAni'), image=self.test_image.name)
        self.studio2 = Studio.objects.create(
            name='Ufotable', slug=slugify('Ufotable'), image=self.test_image.name)

        self.anime_type = AnimeType.objects.create(
            name='TV Show', slug=slugify('TV Show'))

        self.anime = Anime.objects.create(
            title=self.title,
            type=self.anime_type,
            premiere=datetime.date.today(),
            episodes=12,
            image=self.image,
            description=self.description)

        self.anime2 = Anime.objects.create(
            type=self.anime_type,
            premiere=datetime.date.today(),
            episodes=12,)

        self.anime.genre.set([self.genre1.pk, self.genre2.pk])
        self.anime.theme.set([self.theme1.pk, self.theme2.pk])
        self.anime.studio.set([self.studio1.pk, self.studio2.pk])

    def test_anime_listing(self):
        self.assertEqual(self.anime.title, self.title)
        self.assertEqual(self.anime.type, self.anime_type)
        self.assertEqual(self.anime.premiere, datetime.date.today())
        self.assertEqual(self.anime.episodes, 12)
        self.assertEqual(self.anime.studio.count(), 2)
        self.assertEqual(self.anime.genre.count(), 2)
        self.assertEqual(self.anime.theme.count(), 2)

    def test_string_representation(self):
        self.assertEqual(str(self.anime), str(self.title))
        self.assertEqual(str(self.anime2), 'Name does not exist')
        self.assertEqual(str(self.anime_type), 'TV Show')
        self.assertEqual(str(self.studio1), 'KyoAni')

    def test_get_description_success(self):
        self.assertEqual(self.anime.get_desc(), self.description)

    def test_get_description_fail(self):
        self.assertEqual(self.anime2.get_desc(), "No description")

    def test_delete(self):
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Title.objects.count(), 1)
        self.anime.delete()
        self.assertEqual(Image.objects.count(), 0)
        self.assertEqual(Title.objects.count(), 0)


class RelationsTests(TestCase):
    def setUp(self) -> None:
        self.anime = Anime.objects.create()
        self.manga = Manga.objects.create()
        self.anime2 = Anime.objects.create()
        self.manga2 = Manga.objects.create()
        self.adaptation = Adaptation.objects.create(
            adaptation=self.anime, based_on=self.manga)
        self.adaptation_reverse = AdaptationReverse.objects.create(
            adaptation=self.manga, based_on=self.anime)
        self.seq_preq_anime = SequelPrequelAnime.objects.create(
            sequel=self.anime, prequel=self.anime2)
        self.seq_preq_manga = SequelPrequelManga.objects.create(
            sequel=self.manga, prequel=self.manga2)

    def test_relation(self):
        self.assertEqual(self.adaptation.adaptation, self.anime)
        self.assertEqual(self.adaptation.based_on, self.manga)

        self.assertEqual(self.adaptation_reverse.adaptation, self.manga)
        self.assertEqual(self.adaptation_reverse.based_on, self.anime)

        self.assertEqual(self.seq_preq_anime.sequel, self.anime)
        self.assertEqual(self.seq_preq_anime.prequel, self.anime2)
        self.assertEqual(self.seq_preq_manga.sequel, self.manga)
        self.assertEqual(self.seq_preq_manga.prequel, self.manga2)


class ImageTests(TestCase):

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def setUp(self) -> None:
        self.test_image = get_temporary_image()
        self.image = Image.objects.create(image=self.test_image)

    def test_create_thumbnail(self):
        self.assertTrue(self.image.thumbnail)

    def test_delete_image(self):
        self.image.image.delete()
        self.assertFalse(self.image.image)
        self.assertFalse(self.image.thumbnail)

    # def test_delete_image_thumbnail(self):
    #     self.anime.image.thumbnail.delete()
    #     self.assertTrue(self.anime.image.image)
    #     self.assertFalse(self.anime.image.thumbnail)

    def tearDown(self):
        try:
            print(f'Delete test folder from {self.__class__.__name__}')
            shutil.rmtree(TEST_DIR)
        except OSError:
            print('Fail to delete test folder')
            pass

class TitleRepresenationTests(TestCase):
    def setUp(self) -> None:
        self.title = Title.objects.create(
            original_name='Tetsugaka Letra', russian_name='первый тест', english_name='first test')

    def test_original_name(self):
        self.assertEqual(str(self.title), self.title.original_name)

    def test_english_name(self):
        self.title.original_name = None

        self.assertEqual(str(self.title), self.title.english_name)

    def test_russian_name(self):
        self.title.original_name = None
        self.title.english_name = None

        self.assertEqual(str(self.title), self.title.russian_name)

    def test_not_exist(self):
        self.title.original_name = None
        self.title.english_name = None
        self.title.russian_name = None

        self.assertEqual(str(self.title), "Name does not exist")
