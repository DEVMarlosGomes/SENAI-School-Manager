# apps/academico/urls.py
from . import views
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
    # Rotas do Professor
    path('professor/turmas/', views.minhas_turmas_view, name='minhas_turmas'),
    path('professor/diario/<int:alocacao_id>/', views.diario_classe_view, name='diario_classe'),
    path('professor/ocorrencia/<int:turma_id>/<int:aluno_id>/', views.registrar_ocorrencia_view, name='registrar_ocorrencia'),
]
