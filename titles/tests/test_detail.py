from django.test import TestCase
from django.apps import apps
from ..models import *
from post.templatetags.urlparams import urlparams
import uuid

# Create your tests here.


class BaseDetailTests(object):
    def setUp(self):
        self.title = Title.objects.create(
            original_name="Tetsugaka Letra",
            russian_name="первый тест",
            english_name="first test",
        )

        self.item = apps.get_model(
            app_label="titles", model_name=self.model
        ).objects.create(
            title=self.title,
        )
        self.url = reverse(f"{self.model}_detail", kwargs={"pk": self.item.pk})
        self.response = self.client.get(self.url)

    def get_url(self, base_url, params):
        return "{base_url}{querystring}".format(base_url=base_url, querystring=params)

    def test_detail_right(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "titles/detail.html")

    def test_detail_wrong(self):
        no_response = self.client.get(f"/{self.model}/12345/")
        self.assertEqual(no_response.status_code, 404)

    def test_queryset_contains(self):
        self.assertTrue(self.item.id, self.response.context["item"]["id"])

    def test_correct_tab(self):
        tab = "related"
        url_filter_name = self.get_url(self.url, urlparams(tab=tab))
        responce_filter_name = self.client.get(
            url_filter_name, HTTP_ACCEPT="application/json", kwargs={"pk": self.item.pk}
        )
        self.assertEqual(responce_filter_name.context["tab"], tab)

    def test_incorrect_tab(self):
        tab = "something wrong"
        url_filter_name = self.get_url(self.url, urlparams(tab=tab))
        responce_filter_name = self.client.get(
            url_filter_name, HTTP_ACCEPT="application/json", kwargs={"pk": self.item.pk}
        )
        self.assertNotEqual(responce_filter_name.context["tab"], tab)
        self.assertEqual(responce_filter_name.context["tab"], "info")

    def test_type(self):
        self.assertEqual(self.response.context["model"], self.model)

    def test_invalid_id(self):
        url = reverse(f"{self.model}_detail", kwargs={"pk": uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class MangaDetailTests(BaseDetailTests, TestCase):
    def setUp(self):
        self.model = "manga"
        super().setUp()


class AnimeDetailTests(BaseDetailTests, TestCase):
    def setUp(self):
        self.model = "anime"
        super().setUp()
