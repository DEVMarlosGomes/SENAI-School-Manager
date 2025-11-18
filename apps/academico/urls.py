# apps/academico/urls.py

from django.urls import path
from .views import (
    cadastro_aluno_view, 
    lista_alunos_view,
    detalhe_aluno_view,
    editar_aluno_view,
    api_alunos, 
    api_aluno_detail,
    consultar_cep  # ← ADICIONE ESTA LINHA
)

urlpatterns = [
    # Gestão de Alunos
    path('alunos/', lista_alunos_view, name='lista_alunos'),
    path('alunos/cadastrar/', cadastro_aluno_view, name='cadastro_aluno'),
    path('alunos/<int:pk>/', detalhe_aluno_view, name='detalhe_aluno'),
    path('alunos/<int:pk>/editar/', editar_aluno_view, name='editar_aluno'),
    
    # API para CRUD de alunos (usado pelo painel da secretaria)
    path('api/alunos/', api_alunos, name='api_alunos'),
    path('api/alunos/<int:pk>/', api_aluno_detail, name='api_aluno_detail'),
    
    # API - Consulta de CEP
    path('api/consultar-cep/', consultar_cep, name='consultar_cep'),  # ← Agora vai funcionar
]
