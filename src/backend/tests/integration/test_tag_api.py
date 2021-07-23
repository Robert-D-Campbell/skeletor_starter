from django.contrib.auth import get_user_model
from tests.utils import CkcAPITestCase, CkcAPIClient
from django.urls import reverse

from rest_framework import status

from recipes.models import Tag

from recipes.serializers import TagSerializer

# Viewset automatically appends action name to url
TAGS_URL = reverse('recipes:tag-list')

class PublicTagApiTests(CkcAPITestCase):
    """Test public tags API"""

    def setUp(self):
        self.client = CkcAPIClient()

    def test_login_required(self):
        """Test user is logged in to retrieve tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(CkcAPITestCase):
    """Test private tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testing@testing.com',
            'testing'
        )
        self.client = CkcAPIClient()
        self.client.force_authenticate(self.user)

    def test_get_tags(self):
        """Test getting tags"""

        Tag.objects.create(user=self.user, name="Vegetarian")
        Tag.objects.create(user=self.user, name="Mediterranean")

        res = self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        #! test that tags returned are for the authenticated user
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Confort food')
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'testing tag'}
        res = self.client.post(TAGS_URL, payload)
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)