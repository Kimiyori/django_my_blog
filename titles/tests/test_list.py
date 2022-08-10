
from django.test import TestCase
from django.urls import reverse, resolve
from django.apps import apps
from titles.models import Anime, Genre, Manga, Title
from django.template.defaultfilters import slugify
from django.urls import reverse, resolve

from post.templatetags.urlparams import urlparams

from ..views import TitleList


class BaseTitleListTests(object):

    def setUp(self):
        self.title = Title.objects.create(
            original_name='Tetsugaka Letra', russian_name='первый тест', english_name='first test')
        self.title2 = Title.objects.create(
            original_name='test', russian_name='первый тест', english_name='first test')
        self.genre1 = Genre.objects.create(
            name='Romance', slug=slugify('Romance'))
        self.genre2 = Genre.objects.create(
            name='Action', slug=slugify('Action'))

        self.modeltype=apps.get_model(app_label='titles',
                                    model_name=self.model)
        self.item = self.modeltype.objects.create(
            title=self.title,
        )
        self.item.genre.set([self.genre1, self.genre2])
        self.item2 = self.modeltype.objects.create(
            title=self.title2,
        )
        self.item2.genre.set([self.genre1])
        self.url = reverse(f'{self.model}_list')
        self.response = self.client.get(self.url)

    def get_url(self, base_url, params):
        return '{base_url}{querystring}'.format(
            base_url=base_url,
            querystring=params
        )
    def test_anime_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_anime_template(self):  # new
        self.assertTemplateUsed(self.response, 'titles/list.html')

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(
            self.response, 'Hi there! I should not be on the page.')

    def test_homepage_url_resolves_homepageview(self):  
        view = resolve(self.url)
        self.assertEqual(
            view.func.__name__,
            TitleList.as_view().__name__
        )
    
    def test_list_items(self):
        values=['id', 'title__original_name','image__thumbnail']
        self.assertQuerysetEqual(self.response.context['list'],self.modeltype.objects.all(
                                                                    ).values(*values).order_by(
                                                                            'title__original_name'))

    def test_no_filter_name(self):
        q=''
        url_filter_name = self.get_url(
            self.url, urlparams(q=q))
        responce_filter_name = self.client.get(
            url_filter_name, HTTP_ACCEPT='application/json')
        self.assertEqual(responce_filter_name.context['query'], q)
        self.assertEqual(responce_filter_name.context['list'].count(), 2)

        self.assertContains(responce_filter_name, self.title.original_name)

    def test_filter_name(self):
        q=self.title.original_name
        url_filter_name = self.get_url(
            self.url, urlparams(q=q))
        responce_filter_name = self.client.get(
            url_filter_name, HTTP_ACCEPT='application/json')
        self.assertEqual(responce_filter_name.context['query'], q)
        self.assertEqual(responce_filter_name.context['list'].count(), 1)
        self.assertContains(responce_filter_name, self.title.original_name)
    
    def test_filter_wrong_name(self):
        q='I\'m not exist'
        url_filter_name = self.get_url(
            self.url, urlparams(q=q))
        responce_filter_name = self.client.get(
            url_filter_name, HTTP_ACCEPT='application/json')
        self.assertEqual(responce_filter_name.context['query'], q)
        self.assertEqual(responce_filter_name.context['list'].count(), 0)
        self.assertNotContains(responce_filter_name, self.title.original_name)

    def test_filter_attributes(self):

        url_filter_attr = self.get_url(
            self.url, urlparams(genre=self.genre2))
        responce_filter_attr = self.client.get(
            url_filter_attr, HTTP_ACCEPT='application/json')
        self.assertEqual(responce_filter_attr.context['list'].count(), 1)
        self.assertEqual(self.response.context['list'].count(), 2)

            
    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, self.item)

    def test_homepage_contains_correct_modelname(self):
        self.assertEqual(self.response.context['model'], self.model.capitalize())

    def test_homepage_contains_correct_modelname(self):
        self.assertNotEqual(self.response.context['model'], 'Wrong Model Name')


class AnimePageTests(BaseTitleListTests, TestCase):
    """
    Tests for animepage
    """

    def setUp(self):
        self.model='anime'
        super().setUp()
        

class MangaPageTests(BaseTitleListTests, TestCase):
    """
    Tests for mangapage
    """

    def setUp(self):
        self.model='manga'
        super().setUp()

