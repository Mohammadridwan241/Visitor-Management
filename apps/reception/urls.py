from django.urls import path

from . import views

app_name = 'reception'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('visits/', views.visit_list, name='visit-list'),
    path('visits/<int:pk>/', views.visit_detail, name='visit-detail'),
    path('scan/', views.scan, name='scan'),
    path('scan/<str:token>/', views.scan_token, name='scan-token'),
    path('visits/<int:pk>/check-in/', views.check_in, name='check-in'),
    path('visits/<int:pk>/check-out/', views.check_out, name='check-out'),
    path('reports/', views.reports, name='reports'),
    path('reports/export.csv', views.export_csv, name='export-csv'),
]
