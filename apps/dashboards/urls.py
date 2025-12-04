from django.urls import path
from .views import ( 
    home, 
    aluno_dashboard_view, 
    professor_dashboard_view, 
    secretaria_dashboard_view, 
    coordenacao_dashboard_view,
    coordenacao_desempenho_view,
    coordenacao_gestao_view,
    coordenacao_comunicacao_view,
    coordenacao_relatorios_view,
    coordenacao_aprovacao_view, # Nova
    aprovar_registro, # Nova
    rejeitar_registro, # Nova
    gestao_alunos_view,
    controle_financeiro_view,
    gestao_documentos_view,
    comunicacao_secretaria_view,
    perfil_view,
    boletim_view,
    api_coordenacao_kpis,
    api_coordenacao_desempenho,
    api_coordenacao_aprovacao,
    api_coordenacao_atividades,
    save_aluno_view,
    delete_aluno_view,
    aluno_financeiro_view
)

urlpatterns = [
    # Página inicial
    path('', home, name='home'),

    # Dashboards principais
    path('aluno/dashboard/', aluno_dashboard_view, name='aluno_dashboard'),
    path('professor/dashboard/', professor_dashboard_view, name='professor_dashboard'),
    path('secretaria/dashboard/', secretaria_dashboard_view, name='secretaria_dashboard'),
    path('coordenacao/dashboard/', coordenacao_dashboard_view, name='coordenacao_dashboard'),

    # Páginas de Coordenação
    path('coordenacao/desempenho/', coordenacao_desempenho_view, name='coordenacao_desempenho'),
    path('coordenacao/gestao/', coordenacao_gestao_view, name='coordenacao_gestao'),
    path('coordenacao/comunicacao/', coordenacao_comunicacao_view, name='coordenacao_comunicacao'),
    path('coordenacao/relatorios/', coordenacao_relatorios_view, name='coordenacao_relatorios'),
    
    # Sistema de Aprovação (Novo)
    path('coordenacao/aprovacao/', coordenacao_aprovacao_view, name='coordenacao_aprovacao'),
    path('coordenacao/aprovacao/aprovar/<int:pk>/', aprovar_registro, name='aprovar_registro'),
    path('coordenacao/aprovacao/rejeitar/<int:pk>/', rejeitar_registro, name='rejeitar_registro'),

    # APIs para Gestão de Alunos (Salvar e Deletar)
    path('api/gestao/aluno/save/', save_aluno_view, name='save_aluno'),
    path('api/gestao/aluno/delete/<int:pk>/', delete_aluno_view, name='delete_aluno'),

    # Funcionalidades do aluno
    path('aluno/boletim/', boletim_view, name='boletim'),
    path('aluno/financeiro/', aluno_financeiro_view, name='aluno_financeiro'),

    # Funções administrativas
    path('gestao/alunos/', gestao_alunos_view, name='gestao_alunos'),
    path('gestao/documentos/', gestao_documentos_view, name='gestao_documentos'),
    path('controle/financeiro/', controle_financeiro_view, name='controle_financeiro'),
    path('comunicacao/secretaria/', comunicacao_secretaria_view, name='comunicacao_secretaria'),

    # Perfil do usuário
    path('perfil/', perfil_view, name='perfil'),

    # APIs Coordenação (Placeholders)
    path('api/coordenacao/kpis/', api_coordenacao_kpis, name='api_coordenacao_kpis'),
    path('api/coordenacao/desempenho/', api_coordenacao_desempenho, name='api_coordenacao_desempenho'),
    path('api/coordenacao/aprovacao/', api_coordenacao_aprovacao, name='api_coordenacao_aprovacao'),
    path('api/coordenacao/atividades/', api_coordenacao_atividades, name='api_coordenacao_atividades'),
]