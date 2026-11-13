from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Patient


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


class AddPatientViewTests(TestCase):
    def test_dashboard_displays_add_patient_form(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Patient')
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="email"')

    def test_dashboard_post_creates_patient(self):
        patient_user = User.objects.create_user(username='newpatientrecord')

        response = self.client.post(
            reverse('dashboard'),
            {
                'user': patient_user.pk,
                'patient_id': 'PAT-002',
                'name': 'New Patient',
                'email': 'newpatient@example.com',
            },
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Patient.objects.filter(name='New Patient').exists())

    def test_edit_patient_updates_record(self):
        patient_user = User.objects.create_user(username='editme')
        patient = Patient.objects.create(
            user=patient_user, patient_id='PAT-010',
            name='Old Name', email='old@example.com',
        )

        response = self.client.post(
            reverse('edit_patient', args=[patient.pk]),
            {
                'user': patient_user.pk,
                'patient_id': 'PAT-010',
                'name': 'New Name',
                'email': 'new@example.com',
            },
        )

        self.assertRedirects(response, reverse('dashboard'))
        patient.refresh_from_db()
        self.assertEqual(patient.name, 'New Name')
        self.assertEqual(patient.email, 'new@example.com')


class DashboardPatientListTests(TestCase):
    def test_dashboard_shows_saved_patient_details(self):
        patient_user = User.objects.create_user(username='dashboardpatient')
        Patient.objects.create(
            user=patient_user,
            patient_id='PAT-001',
            name='Jordan Patient',
            email='jordan@example.com',
            phone_number='5551234567',
        )

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PAT-001')
        self.assertContains(response, 'Jordan Patient')
        self.assertContains(response, 'jordan@example.com')
        self.assertContains(response, '5551234567')
        self.assertContains(response, 'Active')
        self.assertNotContains(response, 'Jane Smith')


class PatientAdminTests(TestCase):
    def test_patient_admin_lists_saved_patient(self):
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='A-strong-passphrase-928!',
        )
        patient_user = User.objects.create_user(username='patient')
        Patient.objects.create(
            user=patient_user,
            name='Jordan Patient',
            email='jordan@example.com',
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse('admin:patients_patient_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jordan Patient')
        self.assertContains(response, 'jordan@example.com')
