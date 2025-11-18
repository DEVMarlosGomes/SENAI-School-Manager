"""
URL configuration for school_manager project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.usuarios.views import redirecionar_dashboard, home_view

urlpatterns = [
    # Painel administrativo
    path('admin/', admin.site.urls),

    # Redirecionamento padrão após login (para o dashboard correto)
    path('accounts/profile/', redirecionar_dashboard, name='redirecionar_dashboard'),

    # URLs de autenticação padrão do Django (login, logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Apps
    path('usuarios/', include('apps.usuarios.urls')),
    path('academico/', include('apps.academico.urls')),  # ← CEP pode ficar aqui
    path('dashboards/', include('apps.dashboards.urls')),

    # Página inicial (landing page com login e cadastro)
    path('', home_view, name='home'),
]

# Servir arquivos estáticos e de mídia no ambiente local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
