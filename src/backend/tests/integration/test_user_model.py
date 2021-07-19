
from tests.utils import CkcAPITestCase
from django.contrib.auth import get_user_model

class UserModelTests(CkcAPITestCase):
    def test_user_creation_with_successful_email(self):
        """ Test user creation with successful email"""
        email = 'test@test.com'
        password = 'test'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))