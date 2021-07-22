from django.contrib.auth import authenticate, login
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import views, status, generics, authentication, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.serializers import LoginSerializer, UserSerializer, AuthTokenSerializer


# TODO: Add to api docs ??
class LoginView(views.APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=self.request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            email=serializer.validated_data.get('email'),
            password=serializer.validated_data.get('password')
        )

        if user is not None:
            # Set expiry (in seconds) BEFORE inactivity logs you out.
            if serializer.validated_data['remember_me']:
                expiry = 60 * 60 * 24 * 7 * 2  # 2 weeks
            else:
                expiry = 0  # Session only cookie
            request.session.set_expiry(expiry)  # set_expiry must be called before login!

            login(request, user)

            return Response(status=status.HTTP_200_OK)
        else:
            raise ValidationError({"non_field_errors": ["Incorrect login information."]})

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user
