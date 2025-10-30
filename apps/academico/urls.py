# apps/academico/urls.py

from django.urls import path
# Importe a view de cadastro (assumindo que está em apps/dashboards/views.py por enquanto)
from apps.dashboards.views import cadastro_aluno_view 

urlpatterns = [
    # Rota 6: Cadastro de Alunos (acessada pelo botão 'Novo Aluno')
    path('alunos/cadastrar/', cadastro_aluno_view, name='cadastro_aluno'),
    
    # ... outras rotas de gestão (editar, listar, etc.) viriam aqui
]