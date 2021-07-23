from django.contrib.auth import get_user_model
from tests.utils import CkcAPITestCase, CkcAPIClient
from django.urls import reverse

from rest_framework import status

from recipes.models import Ingredient

from recipes.serializers import IngredientSerializer

# Viewset automatically appends action name to url
INGREDIENTS_URL = reverse('recipes:ingredient-list')

class PublicIngredientApiTests(CkcAPITestCase):
    """Test public ingredients API"""

    def setUp(self):
        self.client = CkcAPIClient()

    def test_login_required(self):
        """Test user is logged in to retrieve ingredients"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(CkcAPITestCase):
    """Test private ingredients API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testing@testing.com',
            'testing'
        )
        self.client = CkcAPIClient()
        self.client.force_authenticate(self.user)

    def test_get_ingredients(self):
        """Test getting ingredients"""

        Ingredient.objects.create(user=self.user, name="Rice")
        Ingredient.objects.create(user=self.user, name="Onion")

        res = self.client.get(INGREDIENTS_URL)
        
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test ingredients returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'testpass'
        )
        Ingredient.objects.create(user=user2, name='Fruity')
        ingredient = Ingredient.objects.create(user=self.user, name='Confort food')
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test creating a new ingredient"""
        payload = {'name': 'testing ingredient'}
        res = self.client.post(INGREDIENTS_URL, payload)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating a new ingredient with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)