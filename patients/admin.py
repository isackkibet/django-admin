from django.contrib import admin

from .models import Appointment, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'name', 'email', 'phone_number', 'gender', 'age', 'created_at')
    search_fields = ('patient_id', 'name', 'email', 'phone_number')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'department', 'doctor', 'appointment_date', 'appointment_time')
    list_filter = ('department', 'appointment_date')
    search_fields = ('patient__name', 'doctor', 'reason')
