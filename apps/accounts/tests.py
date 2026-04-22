from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    def test_receptionist_role_flags(self):
        user = get_user_model().objects.create_user(
            username='rec',
            email='rec@example.com',
            password='pass12345',
            full_name='Receptionist',
            role='RECEPTIONIST',
        )

        self.assertTrue(user.is_receptionist)
        self.assertFalse(user.is_admin)
