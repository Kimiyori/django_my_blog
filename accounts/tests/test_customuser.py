from django.test import TestCase
from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError
# Create your tests here.


class CustomUserTests(TestCase):

    def setUp(self) -> None:
        self.user_model = get_user_model()

    def test_create_user_success(self):
        user = self.user_model.objects.create_user(
            username='test',
            email='test@email.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'test')
        self.assertEqual(user.email, 'test@email.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_invalid_email(self):
        with self.assertRaises(ValidationError,msg='invalid email'):
            self.user_model.objects.create_user(
            username='test',
            email='test!mail.ru',
            password='testpass123'
                                )       

    def test_create_superuser(self):

        admin_user = self.user_model.objects.create_superuser(
            username='superadmin',
            email='superadmin@email.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.assertEqual(admin_user.username, 'superadmin')
        self.assertEqual(admin_user.email, 'superadmin@email.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
    def test_create_superuser_without_is_staff(self):
        with self.assertRaises(ValueError,msg='is_staff=False foe admin user'):
            self.user_model.objects.create_superuser(
            username='superadmin',
            email='superadmin@email.com',
            password='testpass123',
            is_superuser=True
        )
    def test_create_superuser_without_is_superuser(self):
        with self.assertRaises(ValueError,msg='is_superuser=False foe admin user'):
            self.user_model.objects.create_superuser(
            username='superadmin',
            email='superadmin@email.com',
            password='testpass123',
            is_staff=True,
        )

