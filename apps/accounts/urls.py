from django.urls import path

from .views import ReceptionLoginView, ReceptionLogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/', ReceptionLoginView.as_view(), name='login'),
    path('logout/', ReceptionLogoutView.as_view(), name='logout'),
]
