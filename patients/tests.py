from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class RegistrationViewTests(TestCase):
    def test_registration_page_displays_form(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_valid_registration_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse('index'),
            {
                'username': 'newpatient',
                'password1': 'A-strong-passphrase-928!',
                'password2': 'A-strong-passphrase-928!',
            },
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='newpatient').exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_invalid_registration_renders_form_errors(self):
        response = self.client.post(
            reverse('index'),
            {
                'username': 'newpatient',
                'password1': 'different-password-928!',
                'password2': 'not-the-same',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The two password fields didn’t match.')
        self.assertFalse(User.objects.filter(username='newpatient').exists())


class LoginViewTests(TestCase):
    def setUp(self):
        self.password = 'A-strong-passphrase-928!'
        self.user = User.objects.create_user(
            username='existingpatient',
            password=self.password,
        )

    def test_valid_login_authenticates_user(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.user.username, 'password': self.password},
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_invalid_login_displays_error(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.user.username, 'password': 'wrong-password'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password.')
        self.assertNotIn('_auth_user_id', self.client.session)
