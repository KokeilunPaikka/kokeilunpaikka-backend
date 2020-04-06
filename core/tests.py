from django.test import TestCase


# Create your tests here.
class BasicTests(TestCase):
    def test_application_has_admin_login(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
