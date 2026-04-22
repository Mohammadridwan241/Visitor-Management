from django.urls import path

from .views import ApiLogoutView

urlpatterns = [
    path('logout/', ApiLogoutView.as_view(), name='api-logout'),
]
