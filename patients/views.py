from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'patients/index.html')
def login(request):
    return render(request, 'patients/login.html')
def dashboard(request):
    return render(request, 'patients/dashboard.html')

def profile(request):
    return render(request, 'patients/profile.html')

def booking(request):
    return render(request, 'patients/booking.html')