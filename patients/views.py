from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
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


def dashboard(request):
    return render(request, 'patients/dashboard.html')


def profile(request):
    return render(request, 'patients/profile.html')


def booking(request):
    return render(request, 'patients/booking.html')
