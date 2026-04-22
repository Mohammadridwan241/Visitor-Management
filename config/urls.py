from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.visitors.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('reception/', include('apps.reception.urls')),
    path('api/', include('apps.visitors.api_urls')),
    path('api/', include('apps.reception.api_urls')),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='api-token-obtain'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('api/auth/', include('apps.accounts.api_urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
