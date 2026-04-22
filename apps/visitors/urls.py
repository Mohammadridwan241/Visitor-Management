from django.urls import path

from .views import RegistrationSuccessView, register_visit

app_name = 'visitors'

urlpatterns = [
    path('', register_visit, name='register'),
    path('register/', register_visit, name='register'),
    path('register/success/<str:reference_no>/', RegistrationSuccessView.as_view(), name='registration-success'),
]
