
from tests.utils import CkcAPITestCase
from django.contrib.auth import get_user_model

class UserModelTests(CkcAPITestCase):
    def test_user_creation_with_successful_email(self):
        """Test user creation with successful email"""
        email = 'test@test.com'
        password = 'test'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_creation_with_normalized_email(self):
        """Test user creation with normalized email"""
        email = 'test@TEST.COM'
        user = get_user_model().objects.create_user(
            email,
            'Password1!'
        )
        # use upper() to make test fail
        self.assertEqual(user.email, email.lower())

    def test_user_creation_invalid_email(self):
        """Test user creation with None email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'Password1!')