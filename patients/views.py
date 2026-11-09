from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render


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


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm(request)
    return render(request, 'patients/login.html', {'form': form})


def dashboard(request):
    return render(request, 'patients/dashboard.html')


def profile(request):
    return render(request, 'patients/profile.html')


def booking(request):
    return render(request, 'patients/booking.html')
