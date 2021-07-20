from django.urls import reverse
from tests.utils import CkcAPITestCase, CkcAPIClient
from django.contrib.auth import get_user_model


class AdminSiteTests(CkcAPITestCase):

    def setUp(self):
        # create test client
        self.client= CkcAPIClient()
        # add new superuser
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@test.com',
            password='Password1!'
        )
        # log superuser into client
        self.client.force_login(self.admin_user)
        # create regular user
        self.user = get_user_model().objects.create_user(
            first_name='admin',
            last_name='test',
            email='admin@testing.com',
            password='Password1!'
        )


    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:users_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.first_name)
        self.assertContains(res, self.user.last_name)
        self.assertContains(res, self.user.email)


    def test_edit_user_page_works(self):
        resp = self.client.get(reverse('admin:users_user_change', args=[self.user.id]))
        assert resp.status_code == 200