from django.urls import path

from patients import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.userlogin, name='login'),
    path('logout/', views.userlogout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('booking/', views.booking, name='booking'),
]
