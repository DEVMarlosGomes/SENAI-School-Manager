"""
URL configuration for school_manager project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.usuarios.views import redirecionar_dashboard, home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/profile/', redirecionar_dashboard, name='redirecionar_dashboard'),
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('usuarios/', include('apps.usuarios.urls')),
    path('academico/', include('apps.academico.urls')),
    path('dashboards/', include('apps.dashboards.urls')),
    path('relatorios/', include('apps.relatorios.urls')),
    path('pagamentos/', include('apps.payments.urls')),
    path('', home_view, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
