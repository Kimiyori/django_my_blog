from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from .views import TitleList
from .models import *
from django.template.defaultfilters import slugify
from django.test import override_settings
from PIL import Image
import tempfile
import datetime
# Create your tests here.
class AnimePageTests(TestCase):
    def setUp(self):
        url = reverse('anime_list')
        self.response = self.client.get(url)
    def test_anime_status_code(self):
        self.assertEqual(self.response.status_code, 200)
    def test_anime_template(self): # new
        self.assertTemplateUsed(self.response, 'titles/list.html')
    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, 'Anime')
    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.')
    def test_homepage_url_resolves_homepageview(self): # new
        view = resolve('/anime/')
        self.assertEqual(
        view.func.__name__,
        TitleList.as_view().__name__
        )
class MangaPageTests(TestCase):
    def setUp(self):
        url = reverse('manga_list')
        self.response = self.client.get(url)
    def test_anime_status_code(self):
        self.assertEqual(self.response.status_code, 200)
    def test_anime_template(self): # new
        self.assertTemplateUsed(self.response, 'titles/list.html')
    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, 'Manga')
    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.')
    def test_homepage_url_resolves_homepageview(self): # new
        view = resolve('/manga/')
        self.assertEqual(
        view.func.__name__,
        TitleList.as_view().__name__
        )

def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, 'png')
    return temp_file
class MangaTests(TestCase):

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def setUp(self):
        self.title=Title.objects.create(original_name='てすて',russian_name='тест',english_name='test')
        self.manga_type=MangaType.objects.create(name='manga',slug=slugify('test'))

        temp_file = tempfile.NamedTemporaryFile()
        self.test_image = get_temporary_image(temp_file)

        self.author=Author.objects.create(name='Sui',surname='Ishida',pseudonym='Sui Ishida',photo=self.test_image.name)
        
        self.publisher1=Publisher.objects.create(name='Kodansha',slug=slugify('Kodansha'),image=self.test_image.name)
        self.publisher2=Publisher.objects.create(name='Shueisha',slug=slugify('Shueisha'),image=self.test_image.name)

        self.genre1=Genre.objects.create(name='Romance',slug=slugify('Romance'))
        self.genre2=Genre.objects.create(name='Action',slug=slugify('Action'))

        self.theme1=Theme.objects.create(name='School',slug=slugify('School'))
        self.theme2=Theme.objects.create(name='Garem',slug=slugify('Garem'))

        self.magazine1=Magazine.objects.create(name='Shounen Jump',slug=slugify('Shounen Jump'))
        self.magazine2=Magazine.objects.create(name='Jump +',slug=slugify('Jump +'))

        self.demographic=Demographic.objects.create(name='Shounen',slug=slugify('Shounen'))
        self.text="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eu lectus arcu. Donec sit amet orci eget sapien tempor vehicula. 
        Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Quisque vitae pellentesque nibh, nec fermentum tortor.
         Nullam bibendum felis non magna pretium dapibus. Donec ex tellus, rhoncus at volutpat non, feugiat vel mauris. Nunc eu euismod arcu, sed feugiat nibh.
          Etiam ac placerat velit, et varius velit. Cras sit amet rutrum metus. Sed nibh ex, gravida in vulputate ut, eleifend in est."""
        self.manga = Manga.objects.create(
        title=self.title,
        type=self.manga_type,
        author=self.author,
        premiere=datetime.date.today(),
        volumes=12,
        chapters=96,
        demographic=self.demographic,
        image=self.test_image.name,
        description=self.text
        )
        self.manga.publisher.set([self.publisher1.pk,self.publisher2.pk])
        self.manga.genre.set([self.genre1.pk,self.genre2.pk])
        self.manga.theme.set([self.theme1.pk,self.theme2.pk])
        self.manga.magazine.set([self.magazine1.pk,self.magazine2.pk])

        self.studio1=Studio.objects.create(name='KyoAni',slug=slugify('KyoAni'),image=self.test_image.name)
        self.studio2=Studio.objects.create(name='Ufotable',slug=slugify('Ufotable'),image=self.test_image.name)

        self.anime_type=AnimeType.objects.create(name='TV Show',slug=slugify('TV Show'))

        self.anime=Anime.objects.create(
        title=self.title,
        type=self.anime_type,
        author=self.author,
        source=self.manga,
        premiere=datetime.date.today(),
        episodes=12,
        image=self.test_image.name,
        description=self.text)

        self.anime.genre.set([self.genre1.pk,self.genre2.pk])
        self.anime.theme.set([self.theme1.pk,self.theme2.pk])
        self.anime.studio.set([self.studio1.pk,self.studio2.pk])

    def test_manga_listing(self):
        self.assertEqual(self.manga.title, self.title)
        self.assertEqual(self.manga.author, self.author)
        self.assertEqual(self.manga.type, self.manga_type)
        self.assertEqual(self.manga.premiere, datetime.date.today())
        self.assertEqual(self.manga.volumes, 12)
        self.assertEqual(self.manga.chapters, 96)
        self.assertEqual(self.manga.demographic, self.demographic)
        self.assertEqual(self.manga.description, self.text)
        self.assertEqual(self.manga.publisher.count(), 2)
        self.assertEqual(self.manga.genre.count(), 2)
        self.assertEqual(self.manga.theme.count(), 2)
        self.assertEqual(self.manga.magazine.count(), 2)
        self.assertEqual(self.manga.image, self.test_image)
    
    def test_anime_listing(self):
        self.assertEqual(self.anime.title, self.title)
        self.assertEqual(self.anime.author, self.author)
        self.assertEqual(self.anime.type, self.anime_type)
        self.assertEqual(self.anime.premiere, datetime.date.today())
        self.assertEqual(self.anime.episodes, 12)
        self.assertEqual(self.anime.source, self.manga)
        self.assertEqual(self.anime.description, self.text)
        self.assertEqual(self.anime.studio.count(), 2)
        self.assertEqual(self.anime.genre.count(), 2)
        self.assertEqual(self.anime.theme.count(), 2)
        self.assertEqual(self.anime.image, self.test_image)

    def test_anime_detail(self):
        response = self.client.get(reverse('anime_detail', args=[self.anime.pk]))
        no_response = self.client.get('/anime/12345/')
        self.assertEqual(no_response.status_code, 404)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.title)
        self.assertTemplateUsed(response, 'titles/detail.html')
    def test_manga_detail(self):
        response = self.client.get(reverse('manga_detail', args=[self.manga.pk]))
        no_response = self.client.get('/manga/12345/')
        self.assertEqual(no_response.status_code, 404)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.title)
        self.assertTemplateUsed(response, 'titles/detail.html')
