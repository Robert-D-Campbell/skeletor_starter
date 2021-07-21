from dj_rest_auth.serializers import PasswordResetSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
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
