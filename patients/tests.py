from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.test import override_settings
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Appointment, Patient, Payment


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
    def setUp(self):
        self.client.force_login(
            User.objects.create_user(username='staffuser', is_staff=True)
        )

    def test_dashboard_displays_add_patient_form(self):
        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Patient')
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="email"')

    def test_dashboard_post_creates_patient(self):
        patient_user = User.objects.create_user(username='newpatientrecord')

        response = self.client.post(
            reverse('admin_dashboard'),
            {
                'user': patient_user.pk,
                'patient_id': 'PAT-002',
                'name': 'New Patient',
                'email': 'newpatient@example.com',
            },
        )

        self.assertRedirects(response, reverse('admin_dashboard'))
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

        self.assertRedirects(response, reverse('admin_dashboard'))
        patient.refresh_from_db()
        self.assertEqual(patient.name, 'New Name')
        self.assertEqual(patient.email, 'new@example.com')


class DashboardPatientListTests(TestCase):
    def setUp(self):
        self.client.force_login(
            User.objects.create_user(username='liststaff', is_staff=True)
        )

    def test_dashboard_shows_saved_patient_details(self):
        patient_user = User.objects.create_user(username='dashboardpatient')
        Patient.objects.create(
            user=patient_user,
            patient_id='PAT-001',
            name='Jordan Patient',
            email='jordan@example.com',
            phone_number='5551234567',
        )

        response = self.client.get(reverse('admin_dashboard'))

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


class PatientApiTests(TestCase):
    def test_patient_list_is_available_in_a_browser(self):
        response = self.client.get(reverse('patient-list'), HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('text/html'))


class PaymentViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='paymentuser', password='test-password')
        self.client.force_login(user)

    def test_payment_form_is_available_to_logged_in_user(self):
        response = self.client.get(reverse('make_payment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="patient_name"')
        self.assertContains(response, 'name="phone_number"')
        self.assertContains(response, 'name="amount"')

    @override_settings(
        MPESA_CALLBACK_URL='https://example.com/mpesa/callback/',
        MPESA_CONSUMER_KEY='test-key',
        MPESA_CONSUMER_SECRET='test-secret',
        MPESA_PASSKEY='test-passkey',
    )
    @patch('patients.views.MpesaClient')
    def test_valid_payment_starts_stk_push_and_saves_checkout_id(self, mpesa_client):
        mpesa_client.return_value.stk_push.return_value = SimpleNamespace(
            response_code='0',
            response_description='Success',
            checkout_request_id='ws_CO_123',
        )

        response = self.client.post(
            reverse('make_payment'),
            {
                'patient_name': 'Jordan Patient',
                'phone_number': '0712345678',
                'amount': '500',
            },
        )

        self.assertRedirects(response, reverse('dashboard'))
        mpesa_client.return_value.stk_push.assert_called_once_with(
            '0712345678',
            500,
            'Hospital Payment',
            'Hospital services',
            'https://example.com/mpesa/callback/',
        )
        payment = Payment.objects.get(transaction_id='ws_CO_123')
        self.assertEqual(payment.patientname, 'Jordan Patient')
        self.assertEqual(payment.phone_number, '0712345678')
        self.assertEqual(payment.amount, 500)

    @override_settings(
        MPESA_CALLBACK_URL='https://example.com/mpesa/callback/',
        MPESA_CONSUMER_KEY='test-key',
        MPESA_CONSUMER_SECRET='test-secret',
        MPESA_PASSKEY='test-passkey',
    )
    @patch('patients.views.MpesaClient')
    def test_success_message_is_shown_on_dashboard_after_payment(self, mpesa_client):
        mpesa_client.return_value.stk_push.return_value = SimpleNamespace(
            response_code='0',
            response_description='Success',
            checkout_request_id='ws_CO_456',
        )

        response = self.client.post(
            reverse('make_payment'),
            {
                'patient_name': 'Jordan Patient',
                'phone_number': '0712345678',
                'amount': '500',
            },
            follow=True,
        )

        self.assertContains(
            response, 'Payment initiated successfully. Please complete it on your phone.'
        )

    @override_settings(
        MPESA_CALLBACK_URL='https://example.com/mpesa/callback/',
        MPESA_CONSUMER_KEY='test-key',
        MPESA_CONSUMER_SECRET='test-secret',
        MPESA_PASSKEY='test-passkey',
    )
    @patch('patients.views.MpesaClient')
    def test_fractional_amount_is_rejected_without_calling_mpesa(self, mpesa_client):
        response = self.client.post(
            reverse('make_payment'),
            {
                'patient_name': 'Jordan Patient',
                'phone_number': '0712345678',
                'amount': '500.50',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'whole-number amount')
        mpesa_client.return_value.stk_push.assert_not_called()
        self.assertFalse(Payment.objects.exists())


class HomePageTests(TestCase):
    def test_public_homepage_has_registration_and_login(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Patient Registration')
        self.assertContains(response, 'Log in')
        self.assertContains(response, 'Our services')
        self.assertNotContains(response, 'Dashboard')
        self.assertNotContains(response, 'Patient records')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('dashboard')
        )

    def test_admin_dashboard_requires_staff(self):
        self.client.force_login(User.objects.create_user(username='notstaff'))

        response = self.client.get(reverse('admin_dashboard'))

        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('admin_dashboard')
        )

    def test_patient_login_goes_to_patient_portal(self):
        user = User.objects.create_user(
            username='portalpatient', password='A-strong-passphrase-928!'
        )

        response = self.client.post(
            reverse('login'), {'username': user.username, 'password': 'A-strong-passphrase-928!'}
        )

        self.assertRedirects(response, reverse('dashboard'))

    def test_staff_login_goes_to_admin_dashboard(self):
        user = User.objects.create_user(
            username='portalstaff', password='A-strong-passphrase-928!', is_staff=True
        )

        response = self.client.post(
            reverse('login'), {'username': user.username, 'password': 'A-strong-passphrase-928!'}
        )

        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_staff_is_redirected_from_patient_portal(self):
        self.client.force_login(User.objects.create_user(username='staffredirect', is_staff=True))

        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(response, reverse('admin_dashboard'))


class NavigationTests(TestCase):
    def test_guest_navbar_shows_register_and_login_only(self):
        response = self.client.get(reverse('index'))

        self.assertContains(response, 'Patient Registration')
        self.assertContains(response, 'Log in')
        self.assertNotContains(response, 'Payment history')
        self.assertNotContains(response, 'Admin Dashboard')

    def test_patient_navbar_shows_every_main_section(self):
        self.client.force_login(User.objects.create_user(username='navpatient'))

        response = self.client.get(reverse('dashboard'))

        self.assertContains(response, 'My Portal')
        self.assertContains(response, 'Make a payment')
        self.assertContains(response, 'Payment history')
        self.assertContains(response, 'View appointments')
        self.assertContains(response, 'Medical Records')
        self.assertContains(response, 'My profile')
        self.assertContains(response, 'Log out')
        self.assertNotContains(response, 'Admin Dashboard')

    def test_admin_navbar_shows_management_sections(self):
        self.client.force_login(User.objects.create_superuser(
            username='navadmin', password='A-strong-passphrase-928!'
        ))

        response = self.client.get(reverse('admin_dashboard'))

        self.assertContains(response, 'Admin Dashboard')
        self.assertContains(response, 'Manage Patients')
        self.assertContains(response, 'All appointments')
        self.assertContains(response, 'All payments')
        self.assertContains(response, 'Django Admin')


class MedicalRecordsTests(TestCase):
    def test_medical_records_requires_login(self):
        response = self.client.get(reverse('medical_records'))

        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('medical_records')
        )

    def test_medical_records_shows_patient_details(self):
        user = User.objects.create_user(username='recorduser')
        Patient.objects.create(
            user=user, patient_id='PAT-M1', name='Record Patient',
            email='record@example.com', phone_number='0700000001',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('medical_records'))

        self.assertContains(response, 'PAT-M1')
        self.assertContains(response, 'Record Patient')
        self.assertContains(response, 'record@example.com')


class AppointmentAndPaymentHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='historyuser')
        self.patient = Patient.objects.create(
            user=self.user, patient_id='PAT-H1', name='History Patient',
            email='history@example.com',
        )
        self.client.force_login(self.user)

    def test_booking_saves_appointment_and_shows_it_in_list(self):
        response = self.client.post(reverse('booking'), {
            'patient': self.patient.pk,
            'department': 'cardiology',
            'doctor': 'Dr Amina',
            'appointment_date': '2026-12-01',
            'appointment_time': '09:30',
            'reason': 'Chest pain review',
        })

        self.assertRedirects(response, reverse('appointment_list'))
        self.assertTrue(Appointment.objects.filter(patient=self.patient).exists())
        self.assertContains(self.client.get(reverse('appointment_list')), 'Dr Amina')

    def test_payment_history_only_shows_the_logged_in_users_payments(self):
        Payment.objects.create(
            user=self.user, patientname='History Patient', amount=200,
            transaction_id='ws_co_mine',
        )
        Payment.objects.create(
            patientname='Other Patient', amount=900, transaction_id='ws_co_theirs'
        )

        response = self.client.get(reverse('payment_history'))

        self.assertContains(response, 'ws_co_mine')
        self.assertNotContains(response, 'ws_co_theirs')

    def test_admin_sees_all_payments(self):
        self.user.is_staff = True
        self.user.save()
        Payment.objects.create(
            patientname='Other Patient', amount=900, transaction_id='ws_co_theirs'
        )

        response = self.client.get(reverse('payment_history'))

        self.assertContains(response, 'ws_co_theirs')
        self.assertContains(response, 'All payments')


class MpesaConfigurationTests(TestCase):
    def test_sandbox_defaults_are_configured(self):
        self.assertEqual(settings.MPESA_ENVIRONMENT, 'sandbox')
        self.assertEqual(settings.MPESA_EXPRESS_SHORTCODE, '174379')
        self.assertEqual(settings.MPESA_SHORTCODE, '600982')
        self.assertEqual(settings.MPESA_INITIATOR_USERNAME, 'testapi')
        self.assertEqual(settings.MPESA_TEST_PHONE, '254708374149')

    @override_settings(MPESA_CONSUMER_KEY='', MPESA_CONSUMER_SECRET='')
    def test_mpesa_test_command_reports_missing_consumer_credentials(self):
        stdout = StringIO()
        stderr = StringIO()

        call_command('mpesa_test', stdout=stdout, stderr=stderr)

        self.assertIn('Missing required settings', stderr.getvalue())
