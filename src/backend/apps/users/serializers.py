from dj_rest_auth.serializers import PasswordResetSerializer
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from utils import email


User = get_user_model()


class PasswordResetFormCustomEmail(PasswordResetForm):

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, **kwargs):
        email.password_reset(to_email, context['uid'], context['token'])


class PasswordResetCustomEmailSerializer(PasswordResetSerializer):

    password_reset_form_class = PasswordResetFormCustomEmail


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    remember_me = serializers.BooleanField(default=False, required=False)


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
        )
        read_only_fields = ('email',)

class UserSerializer(serializers.ModelSerializer):
    """ Serializer for users object w/ password """

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # override the create function
    def create(self, validated_data):
        """Create a new user with an encrypted password and return it"""
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set a passweord, and return it"""
        password=validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
            
        return user
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = ('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs