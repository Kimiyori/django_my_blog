from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Profile
from titles.tests.test_models import get_temporary_image
from django.test import override_settings
import shutil

# Create your tests here.

TEST_DIR = "test_data"


class CustomUserTests(TestCase):
    def setUp(self) -> None:
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="test", email="test@email.com", password="testpass123"
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_create_profile_success(self):
        self.assertTrue(self.profile)
        self.assertEqual(self.profile.user.id, self.user.id)
        self.assertTrue(Profile.objects.count(), 1)

    def test_str(self):
        self.assertEqual(str(self.profile), f"Profile for user {self.user}")

    @override_settings(MEDIA_ROOT=(TEST_DIR + "/media"))
    def test_img(self):
        image = get_temporary_image()
        self.assertEqual(image.height, 1000)
        self.profile.photo = image
        self.profile.save()
        self.assertTrue(Profile.objects.get(user=self.user).photo)
        self.assertEqual(Profile.objects.get(user=self.user).photo.height, 400)

        try:
            print(f"Delete test folder from {self.__class__.__name__}")
            shutil.rmtree(TEST_DIR)
        except OSError:
            print("Fail to delete test folder")
            pass
