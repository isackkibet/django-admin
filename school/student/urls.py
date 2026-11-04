from django.urls import path

from school.student import views


urlpatterns = [
    path('', views.student, name='student'),
]
