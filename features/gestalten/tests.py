from django.contrib import auth


class GestaltMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.gestalt = auth.get_user_model().objects.create(
                email='test@example.org', username='test').gestalt


class OtherGestaltMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.other_gestalt = auth.get_user_model().objects.create(
                email='test2@example.org', username='test2').gestalt


class AuthenticatedMixin(GestaltMixin):
    def setUp(self):
        super().setUp()
        self.client.force_login(
                self.gestalt.user, 'django.contrib.auth.backends.ModelBackend')
