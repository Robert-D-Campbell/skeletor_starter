from django.contrib.auth import get_user_model
from tests.utils import CkcAPITestCase
from recipes import models

def sample_user(email='testing@testing.com', password='testing'):
    """Create sample user"""
    return get_user_model().objects.create_user(email, password)
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

    def test_superuser_creation(self):
        """Test superuser creation is successful"""
        user= get_user_model().objects.create_superuser(
            'test@test.com',
            'Password1!'
        )
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_superuser_creation_invalid_permissions(self):
        """Test superuser creation with False permissions raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
            email='test@test.com',
            password='Password1!',
            is_staff=False,
            is_superuser=False
        )

    def test_tag_str(self):
        """Test the Tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegetarian'
        )

        self.assertEqual(str(tag), tag.name)
