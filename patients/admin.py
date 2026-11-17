from django.contrib import admin

from .models import Appointment, Patient, Payment


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'name', 'email', 'phone_number', 'gender', 'age', 'created_at')
    search_fields = ('patient_id', 'name', 'email', 'phone_number')
    list_filter = ('gender',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'department', 'doctor', 'appointment_date', 'appointment_time')
    list_filter = ('department', 'appointment_date')
    search_fields = ('patient__name', 'doctor', 'reason')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'patientname', 'user', 'phone_number', 'amount', 'payment_date')
    search_fields = ('transaction_id', 'patientname', 'phone_number', 'user__username')
    list_filter = ('payment_date',)
    date_hierarchy = 'payment_date'
