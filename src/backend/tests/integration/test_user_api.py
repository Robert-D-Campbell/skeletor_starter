from django.contrib.auth import get_user_model
from tests.utils import CkcAPITestCase, CkcAPIClient
from django.urls import reverse

from rest_framework import status

# Create the user creation url and assign it to constant
CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')

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

    # Sanity check by not creating user
    def test_create_auth_token(self):
        """Test that a token is created for the user"""
        payload = {'email': 'testing@testing.com', 'password': 'testing'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # Sanity check by changing user password to correct value
    def test_create_token_invalid_credentials(self):
        """Test that the token is not created if invalid credentials are passed"""
        create_user(email='testing@testing.com', password='testing')
        payload = {'email': 'testing@testing.com', 'password': 'wrongPassword'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Sanity check by creating a user then log in
    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {'email': 'testing@testing.com', 'password': 'testing'}
        res=self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Sanity check by creating a user then log in or enter valid email and password 
    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': '', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)