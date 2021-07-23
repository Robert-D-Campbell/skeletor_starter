from django.contrib.auth import get_user_model
from tests.utils import CkcAPITestCase, CkcAPIClient
from django.urls import reverse

from rest_framework import status, test

from recipes.models import Recipe

from recipes.serializers import RecipeSerializer


# Viewset automatically appends action name to url
RECIPES_URL = reverse('recipes:recipe-list')


def sample_recipe(user, **kwargs):
    """Create and return sample recipe"""

    defaults = {
        'title': 'sample recipe',
        'time_minutes': 9,
        'price': 9.99
    } 
    defaults.update(kwargs)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(CkcAPITestCase):
    """Test public recipe API"""

    def setUp(self):
        self.client = CkcAPIClient()

    def test_login_required(self):
        """Test user is logged in to retrieve recipes"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(CkcAPITestCase):
    """Test private recipes API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testing@testing.com',
            'testing'
        )
        self.client = CkcAPIClient()
        self.client.force_authenticate(self.user)

    def test_get_recipes(self):
        """Test getting recipes"""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test recipes returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'testpass'
        )
        sample_recipe(user=self.user)
        sample_recipe(user=user2)
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_invalid(self):
        """Test creating a new recipe with invalid payload"""
        payload = {'title': ''}
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)