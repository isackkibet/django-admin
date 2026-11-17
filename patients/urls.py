from django.urls import include, path
from rest_framework.routers import DefaultRouter

from patients import views


router = DefaultRouter()
router.register(r'patients', views.PatientViewSet, basename='patient')

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.userlogin, name='login'),
    path('logout/', views.userlogout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('medical-records/', views.medical_records, name='medical_records'),
    path('profile/', views.profile, name='profile'),
    path('booking/', views.booking, name='booking'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('payments/', views.payment_history, name='payment_history'),
    path('patient/<int:pk>/edit/', views.edit_patient, name='edit_patient'),
    path('patient/<int:pk>/delete/', views.delete_patient, name='delete_patient'),
    path('payment/', views.make_payment, name='make_payment'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('', include(router.urls)),
    path('api/', include(router.urls)),
]
