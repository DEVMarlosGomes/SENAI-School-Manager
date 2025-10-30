# apps/dashboards/urls.py

from django.urls import path
from .views import ( 
    home, 
    aluno_dashboard_view, 
    professor_dashboard_view, 
    secretaria_dashboard_view, 
    coordenacao_dashboard_view 
        # Importe a nova view
)

urlpatterns = [
    # Rota da Home (Funciona na raiz do site '/')
    path('', home, name='home'),
    
    # Rota do Dashboard do Professor
    # Este 'name' deve ser idêntico ao que está no template: 'professor_dashboard'
    path('aluno/dashboard/', aluno_dashboard_view, name='aluno_dashboard'),
    path('professor/dashboard/', professor_dashboard_view, name='professor_dashboard'),
    path('secretaria/dashboard/', secretaria_dashboard_view, name='secretaria_dashboard'),
    path('coordenacao/dashboard/', coordenacao_dashboard_view, name='coordenacao_dashboard'),
    
    # ... (outras rotas: aluno_dashboard, secretaria_dashboard, etc.)
]