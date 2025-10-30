"""
URL configuration for school_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# school_manager/urls.py (Principal)

from django.contrib import admin
from django.urls import path, include
# ... outras importações ...

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs de Autenticação (IMPORTANTE para 'login', 'logout')
    path('contas/', include('django.contrib.auth.urls')),
    
    # URLs dos Dashboards (Home e Painéis Internos)
    path('', include('apps.dashboards.urls')),
    
    # URLs do Módulo Acadêmico/Gestão (Onde está o cadastro de aluno)
    path('academico/', include('apps.academico.urls')), 
    
    # ... Se você mantiver o path('entrar/', login_view, name='login'), ele irá sobrescrever a rota padrão do Django
]
