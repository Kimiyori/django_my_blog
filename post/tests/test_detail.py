from uuid import uuid4
from django.test import TestCase
from ..models import *
from ..views import PostDetail
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

# Create your tests here.


class PostDetailTests(TestCase):
    def setUp(self):
        self.title = "Test Post"
        self.user = get_user_model().objects.create_user(
            username="test", password="12test12", email="test@example.com"
        )
        self.post = Post.objects.create(
            title=self.title,
            author=self.user,
            status=Post.DRAFT,
        )

        self.url = reverse("post_detail", args=[self.post.pk])
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template(self):  # new
        self.assertTemplateUsed(self.response, "post/manage/detail.html")

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, "Blog")

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_homepage_url_resolves_homepageview(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, PostDetail.as_view().__name__)

    def test_total_views(self):
        self.assertEqual(self.response.context["total_views"], 0)

    def test_context_post(self):
        self.assertEqual(self.response.context["post"]["id"], self.post.id)
        self.assertEqual(self.response.context["post"]["title"], self.post.title)

    def test_wrong_id(self):
        url = reverse("post_detail", args=[uuid4()])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
