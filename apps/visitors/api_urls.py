from django.urls import path

from .api_views import (
    VisitByReferenceAPIView,
    VisitByTokenAPIView,
    VisitCheckInAPIView,
    VisitCheckOutAPIView,
    VisitDetailAPIView,
    VisitListAPIView,
    VisitRegistrationAPIView,
)

urlpatterns = [
    path('visits/register/', VisitRegistrationAPIView.as_view(), name='api-visit-register'),
    path('visits/', VisitListAPIView.as_view(), name='api-visit-list'),
    path('visits/<int:pk>/', VisitDetailAPIView.as_view(), name='api-visit-detail'),
    path('visits/reference/<str:reference_no>/', VisitByReferenceAPIView.as_view(), name='api-visit-reference'),
    path('visits/qr/<str:token>/', VisitByTokenAPIView.as_view(), name='api-visit-qr'),
    path('visits/<int:pk>/check-in/', VisitCheckInAPIView.as_view(), name='api-visit-check-in'),
    path('visits/<int:pk>/check-out/', VisitCheckOutAPIView.as_view(), name='api-visit-check-out'),
]
