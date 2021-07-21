from django.contrib.auth import get_user_model
from tests.utils import CkcAPITestCase, CkcAPIClient
from django.urls import reverse

from rest_framework import status

# Create the user creation url and assign it to constant
CREATE_USER_URL = reverse('users:create')

def create_user(**kwargs):
    """Helper function to create users"""
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTests(CkcAPITestCase):
    """Test public users API"""

    def setUp(self):
        self.client = CkcAPIClient()

    def test_successful_valid_user_creation(self):
        """Test valid user creation is successful"""
        payload = {
            'email': 'testing@testing.com',
            'password': 'testing',
            'first_name': "testing",
            'last_name': "testing",

        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test bad request when creating a user that already exists """
        payload = {
            'email': 'tester@tester.com',
            'password': 'tester',
            'first_name': "tester",
            'last_name': "tester",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password is longer than 5 characters"""
        payload = {
            'email': 'test@test.com',
            'password': 't',
            'first_name': "test",
            'last_name': "test",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)