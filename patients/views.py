from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PatientForm
from patients.models import Patient


def index(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('dashboard')
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
            return redirect('dashboard')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'patients/login.html', {'error_message': error_message})
    return render(request, 'patients/login.html')


def userlogout(request):
    auth_logout(request)
    return redirect('login')


def _render_dashboard(request, form=None, invalid_edit_form=None, invalid_edit_pk=None):
    patients = list(Patient.objects.select_related('user').order_by('name'))
    for patient in patients:
        if patient.pk == invalid_edit_pk:
            patient.edit_form = invalid_edit_form
        else:
            patient.edit_form = PatientForm(
                instance=patient, auto_id=f'id_edit{patient.pk}_%s'
            )
    return render(request, 'patients/dashboard.html', {
        'patients': patients,
        'form': form or PatientForm(),
        'open_edit_pk': invalid_edit_pk,
    })


def dashboard(request):
    form = None
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    return _render_dashboard(request, form=form)


def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method != 'POST':
        return redirect('dashboard')
    edit_form = PatientForm(
        request.POST, instance=patient, auto_id=f'id_edit{patient.pk}_%s'
    )
    if edit_form.is_valid():
        edit_form.save()
        return redirect('dashboard')
    return _render_dashboard(
        request, invalid_edit_form=edit_form, invalid_edit_pk=patient.pk
    )


def profile(request):
    return render(request, 'patients/profile.html')


def booking(request):
    return render(request, 'patients/booking.html')


def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
    return redirect('dashboard')