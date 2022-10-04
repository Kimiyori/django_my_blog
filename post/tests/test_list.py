from django.test import TestCase
from ..models import *
from ..views import PostList
from django.urls import reverse, resolve

# Create your tests here.


class PostListTests(TestCase):
    def setUp(self):
        self.url = reverse("post_list")
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template(self):  # new
        self.assertTemplateUsed(self.response, "post/list.html")

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, "Blog")

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_homepage_url_resolves_homepageview(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, PostList.as_view().__name__)
