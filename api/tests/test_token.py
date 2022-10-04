from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token


class TestToken(APITestCase):
    def setUp(self):
        self.username = "test_user"
        self.password = "test_pass"
        self.user = get_user_model().objects.create_superuser(
            username=self.username,
            email="superadmin@email.com",
            password=self.password,
            is_staff=True,
            is_superuser=True,
        )
        self.user.save()
        self.token = Token.objects.get(user=self.user)
        self.uri = reverse("anime-list")
        self.data = {
            "title": {
                "original_name": "te1st",
                "english_name": "test2",
                "russian_name": "test3",
            },
        }

    def test_token(self):
        self.assertEqual(self.user.auth_token, self.token)

    def test_auth_success(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + str(self.user.auth_token))
        response = self.client.post(self.uri, data=self.data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_auth_wrong_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + "wrong_token")
        response = self.client.post(self.uri, data=self.data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_get_token_with_url(self):
        data = {"username": self.username, "password": self.password}
        response = self.client.post(reverse("api-token-auth"), data=data)
        self.assertEqual(response.data["token"], str(self.user.auth_token))
