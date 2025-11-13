# apps/dashboards/urls.py

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
    gestao_alunos_view,
    controle_financeiro_view,
    gestao_documentos_view,
    comunicacao_secretaria_view,
    perfil_view,
    materiais_estudo_view,
    boletim_view,
    calendario_view,
    avisos_eventos_view,
    api_coordenacao_kpis,
    api_coordenacao_desempenho,
    api_coordenacao_aprovacao,
    api_coordenacao_atividades,
)

urlpatterns = [
    # -------------------------
    # Página inicial
    # -------------------------
    path('', home, name='home'),
    
    # -------------------------
    # Dashboards principais
    # -------------------------
    path('aluno/dashboard/', aluno_dashboard_view, name='aluno_dashboard'),
    path('professor/dashboard/', professor_dashboard_view, name='professor_dashboard'),
    path('secretaria/dashboard/', secretaria_dashboard_view, name='secretaria_dashboard'),
    path('coordenacao/dashboard/', coordenacao_dashboard_view, name='coordenacao_dashboard'),
    
    # -------------------------
    # Páginas de Coordenação
    # -------------------------
    path('coordenacao/desempenho/', coordenacao_desempenho_view, name='coordenacao_desempenho'),
    path('coordenacao/gestao/', coordenacao_gestao_view, name='coordenacao_gestao'),
    path('coordenacao/comunicacao/', coordenacao_comunicacao_view, name='coordenacao_comunicacao'),
    path('coordenacao/relatorios/', coordenacao_relatorios_view, name='coordenacao_relatorios'),

    # -------------------------
    # Funcionalidades do aluno
    # -------------------------
    path('aluno/materiais/', materiais_estudo_view, name='materiais_estudo'),
    path('aluno/boletim/', boletim_view, name='boletim'),
    path('aluno/calendario/', calendario_view, name='calendario'),
    path('aluno/avisos-eventos/', avisos_eventos_view, name='avisos_eventos'),

    # -------------------------
    # Funções administrativas
    # -------------------------
    path('gestao/alunos/', gestao_alunos_view, name='gestao_alunos'),
    path('gestao/documentos/', gestao_documentos_view, name='gestao_documentos'),
    path('controle/financeiro/', controle_financeiro_view, name='controle_financeiro'),
    path('comunicacao/secretaria/', comunicacao_secretaria_view, name='comunicacao_secretaria'),

    # -------------------------
    # Perfil do usuário
    # -------------------------
    path('perfil/', perfil_view, name='perfil'),
    # API Coordenacao
    path('api/coordenacao/kpis/', api_coordenacao_kpis, name='api_coordenacao_kpis'),
    path('api/coordenacao/desempenho/', api_coordenacao_desempenho, name='api_coordenacao_desempenho'),
    path('api/coordenacao/aprovacao/', api_coordenacao_aprovacao, name='api_coordenacao_aprovacao'),
    path('api/coordenacao/atividades/', api_coordenacao_atividades, name='api_coordenacao_atividades'),
]
