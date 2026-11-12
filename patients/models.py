from django.conf import settings
from django.db import models


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient',
    )
    patient_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=150)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        default='',
    )
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.user.get_username()


class Appointment(models.Model):
    class Department(models.TextChoices):
        GENERAL_MEDICINE = 'general_medicine', 'General Medicine'
        CARDIOLOGY = 'cardiology', 'Cardiology'
        PEDIATRICS = 'pediatrics', 'Pediatrics'
        DENTISTRY = 'dentistry', 'Dentistry'

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
    )
    department = models.CharField(max_length=32, choices=Department.choices)
    doctor = models.CharField(max_length=150, blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date', 'appointment_time']

    def __str__(self):
        return f'{self.patient} - {self.get_department_display()} on {self.appointment_date}'