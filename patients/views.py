from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from django_daraja.mpesa.core import MpesaClient
from django_daraja.mpesa.exceptions import (
    MpesaConfigurationException,
    MpesaConnectionError,
    MpesaError,
    MpesaInvalidParameterException,
)
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .forms import AppointmentForm, PatientForm, ProfileForm
from .models import Appointment, Patient, Payment
from .serializers import PatientSerializer


staff_required = user_passes_test(lambda user: user.is_staff, login_url='login')


def _portal_url(user):
    return 'admin_dashboard' if user.is_staff else 'dashboard'


def home(request):
    return render(request, 'patients/home.html')


def index(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(_portal_url(user))
    else:
        form = UserCreationForm()
    return render(request, 'patients/index.html', {'form': form})


def userlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            next_url = request.POST.get('next', '')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect(_portal_url(user))
        return render(request, 'patients/login.html', {
            'error_message': 'Please enter a correct username and password.',
            'next': request.POST.get('next', ''),
        })
    return render(request, 'patients/login.html', {'next': request.GET.get('next', '')})


def userlogout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    patient = getattr(request.user, 'patient', None)
    appointments = Appointment.objects.filter(patient=patient) if patient else Appointment.objects.none()
    payments = Payment.objects.filter(user=request.user)
    totals = payments.aggregate(total=Sum('amount'))
    return render(request, 'patients/dashboard.html', {
        'patient': patient,
        'appointments': appointments.order_by('appointment_date', 'appointment_time')[:5],
        'payments': payments.order_by('-payment_date')[:5],
        'appointment_count': appointments.count(),
        'payment_count': payments.count(),
        'total_paid': totals['total'] or Decimal('0'),
    })


def _render_admin_dashboard(request, form=None, invalid_edit_form=None, invalid_edit_pk=None):
    patients = list(Patient.objects.select_related('user').order_by('name'))
    for patient in patients:
        if patient.pk == invalid_edit_pk:
            patient.edit_form = invalid_edit_form
        else:
            patient.edit_form = PatientForm(
                instance=patient, auto_id=f'id_edit{patient.pk}_%s'
            )
    totals = Payment.objects.aggregate(total=Sum('amount'))
    return render(request, 'patients/admin_dashboard.html', {
        'patients': patients,
        'form': form or PatientForm(),
        'open_edit_pk': invalid_edit_pk,
        'appointment_count': Appointment.objects.count(),
        'payment_count': Payment.objects.count(),
        'total_paid': totals['total'] or Decimal('0'),
    })


@staff_required
def admin_dashboard(request):
    form = None
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient record added.')
            return redirect('admin_dashboard')
    return _render_admin_dashboard(request, form=form)


@staff_required
def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method != 'POST':
        return redirect('admin_dashboard')
    edit_form = PatientForm(
        request.POST, instance=patient, auto_id=f'id_edit{patient.pk}_%s'
    )
    if edit_form.is_valid():
        edit_form.save()
        messages.success(request, 'Patient record updated.')
        return redirect('admin_dashboard')
    return _render_admin_dashboard(
        request, invalid_edit_form=edit_form, invalid_edit_pk=patient.pk
    )


@staff_required
def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Patient record deleted.')
    return redirect('admin_dashboard')


@login_required
def profile(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    patient = getattr(request.user, 'patient', None)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user
            patient.save()
            messages.success(request, 'Your profile has been saved.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=patient)
    return render(request, 'patients/profile.html', {'form': form, 'patient': patient})


@login_required
def booking(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your appointment request has been recorded.')
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'patients/booking.html', {'form': form})


@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related('patient')
    if not request.user.is_staff:
        appointments = appointments.filter(patient__user=request.user)
    return render(request, 'patients/appointment_list.html', {
        'appointments': appointments,
        'is_admin': request.user.is_staff,
    })


@login_required
def payment_history(request):
    payments = Payment.objects.select_related('user').order_by('-payment_date')
    if not request.user.is_staff:
        payments = payments.filter(user=request.user)
    totals = payments.aggregate(total=Sum('amount'))
    return render(request, 'patients/payment_history.html', {
        'payments': payments,
        'is_admin': request.user.is_staff,
        'total_paid': totals['total'] or Decimal('0'),
    })


@login_required
def medical_records(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    patient = getattr(request.user, 'patient', None)
    return render(request, 'patients/medical_records.html', {'patient': patient})


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [AllowAny]


@login_required
def make_payment(request):
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        amount_value = request.POST.get('amount', '').strip()

        try:
            amount = Decimal(amount_value)
        except InvalidOperation:
            amount = Decimal('0')

        if (
            not patient_name
            or not phone_number
            or not phone_number.isdigit()
            or not 9 <= len(phone_number) <= 12
            or phone_number[-9] not in '17'
            or not amount.is_finite()
            or amount < 1
            or amount > 99999999
        ):
            messages.error(request, 'Enter a patient name, phone number, and valid amount.')
            return render(request, 'patients/make_payment.html')
        if amount != amount.to_integral_value():
            messages.error(request, 'M-Pesa payments must be a whole-number amount.')
            return render(request, 'patients/make_payment.html')

        callback_url = settings.MPESA_CALLBACK_URL
        if not all((
            settings.MPESA_CONSUMER_KEY,
            settings.MPESA_CONSUMER_SECRET,
            settings.MPESA_PASSKEY,
            callback_url,
        )):
            messages.error(
                request,
                'M-Pesa credentials and a callback URL must be configured before payments.',
            )
            return render(request, 'patients/make_payment.html')

        try:
            response = MpesaClient().stk_push(
                phone_number,
                int(amount),
                'Hospital Payment',
                'Hospital services',
                callback_url,
            )
        except (
            MpesaConfigurationException,
            MpesaConnectionError,
            MpesaError,
            MpesaInvalidParameterException,
        ):
            messages.error(request, 'M-Pesa could not start the payment. Please try again.')
            return render(request, 'patients/make_payment.html')

        if str(response.response_code) != '0' or not response.checkout_request_id:
            messages.error(
                request,
                response.response_description or 'M-Pesa did not accept the payment request.',
            )
            return render(request, 'patients/make_payment.html')

        Payment.objects.create(
            user=request.user,
            patientname=patient_name,
            phone_number=phone_number,
            amount=amount,
            transaction_id=response.checkout_request_id,
        )
        messages.success(
            request,
            'Payment initiated successfully. Please complete it on your phone.',
        )
        return redirect(_portal_url(request.user))

    return render(request, 'patients/make_payment.html')


@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            MpesaClient().parse_stk_result(request.body.decode('utf-8'))
        except (ValueError, KeyError, TypeError):
            return HttpResponse('Invalid callback payload', status=400)
    return HttpResponse('OK')
