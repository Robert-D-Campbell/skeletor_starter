from django.contrib.auth import get_user_model
from tests.utils import CkcAPITestCase, CkcAPIClient
from django.urls import reverse

from rest_framework import status

from recipes.models import Tag

from recipes.serializersimport TagSerializer

# Viewset automatically appends action name to url
TAGS_URL = reverse('recipes:tag-list')