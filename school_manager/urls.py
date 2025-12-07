"""
URL configuration for school_manager project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importamos as views personalizadas
from apps.dashboards.views import home 
from apps.usuarios.views import redirecionar_dashboard, logout_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota de Logout personalizada (Prioridade sobre o padrão)
    path('logout/', logout_view, name='logout'),
    
    # Rota para redirecionar login bem-sucedido
    path('accounts/profile/', redirecionar_dashboard, name='redirecionar_dashboard'),
    
    # Rotas de autenticação padrão (recuperação de senha, etc)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Apps do sistema
    path('usuarios/', include('apps.usuarios.urls')),
    path('academico/', include('apps.academico.urls')),
    path('dashboards/', include('apps.dashboards.urls')),
    path('relatorios/', include('apps.relatorios.urls')),
    path('pagamentos/', include('apps.payments.urls')),
    
    # Rota da Página Inicial (Home)
    path('', home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)