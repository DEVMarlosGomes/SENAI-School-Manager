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
    coordenacao_aprovacao_view,
    gestao_alunos_view,
    controle_financeiro_view,
    gestao_documentos_view,
    comunicacao_secretaria_view,
    perfil_view,
    boletim_view,
    calendario_view,
    avisos_eventos_view,
    api_coordenacao_kpis,
    api_coordenacao_desempenho,
    api_coordenacao_aprovacao,
    api_coordenacao_atividades,
    aluno_financeiro_view,
    criar_aviso,
    criar_evento,
    api_avisos_eventos,
    # APIs de Gestão (CRUD)
    save_aluno_view, delete_aluno_view,
    save_turma_view, delete_turma_view,
    save_professor_view, delete_professor_view,
    save_disciplina_view, delete_disciplina_view
)

urlpatterns = [
    # ========================================================
    # 1. PÁGINA INICIAL
    # ========================================================
    path('', home, name='home'),

    # ========================================================
    # 2. DASHBOARDS PRINCIPAIS POR PERFIL
    # ========================================================
    path('aluno/dashboard/', aluno_dashboard_view, name='aluno_dashboard'),
    path('professor/dashboard/', professor_dashboard_view, name='professor_dashboard'),
    path('secretaria/dashboard/', secretaria_dashboard_view, name='secretaria_dashboard'),
    path('coordenacao/dashboard/', coordenacao_dashboard_view, name='coordenacao_dashboard'),

    # ========================================================
    # 3. ROTAS DA COORDENAÇÃO
    # ========================================================
    path('coordenacao/desempenho/', coordenacao_desempenho_view, name='coordenacao_desempenho'),
    path('coordenacao/gestao/', coordenacao_gestao_view, name='coordenacao_gestao'),
    path('coordenacao/comunicacao/', coordenacao_comunicacao_view, name='coordenacao_comunicacao'),
    path('coordenacao/relatorios/', coordenacao_relatorios_view, name='coordenacao_relatorios'),
    path('coordenacao/aprovacao/', coordenacao_aprovacao_view, name='coordenacao_aprovacao'),

    # ========================================================
    # 4. APIS DE GESTÃO ACADÊMICA (CRUD COMPLETO)
    # ========================================================
    
    # Alunos
    path('api/gestao/aluno/save/', save_aluno_view, name='save_aluno'),
    path('api/gestao/aluno/delete/<int:pk>/', delete_aluno_view, name='delete_aluno'),

    # Turmas
    path('api/gestao/turma/save/', save_turma_view, name='save_turma'),
    path('api/gestao/turma/delete/<int:pk>/', delete_turma_view, name='delete_turma'),

    # Professores
    path('api/gestao/professor/save/', save_professor_view, name='save_professor'),
    path('api/gestao/professor/delete/<int:pk>/', delete_professor_view, name='delete_professor'),

    # Disciplinas
    path('api/gestao/disciplina/save/', save_disciplina_view, name='save_disciplina'),
    path('api/gestao/disciplina/delete/<int:pk>/', delete_disciplina_view, name='delete_disciplina'),

    # ========================================================
    # 5. FUNCIONALIDADES DO ALUNO
    # ========================================================
    path('aluno/boletim/', boletim_view, name='boletim'),
    path('aluno/calendario/', calendario_view, name='calendario'),
    path('aluno/avisos-eventos/', avisos_eventos_view, name='avisos_eventos'),
    path('aluno/financeiro/', aluno_financeiro_view, name='aluno_financeiro'),

    # ========================================================
    # 6. FUNÇÕES ADMINISTRATIVAS GERAIS
    # ========================================================
    path('gestao/alunos/', gestao_alunos_view, name='gestao_alunos'),
    path('gestao/documentos/', gestao_documentos_view, name='gestao_documentos'),
    path('controle/financeiro/', controle_financeiro_view, name='controle_financeiro'),
    path('comunicacao/secretaria/', comunicacao_secretaria_view, name='comunicacao_secretaria'),

    # ========================================================
    # 7. PERFIL DO USUÁRIO
    # ========================================================
    path('perfil/', perfil_view, name='perfil'),

    # ========================================================
    # 8. APIS AUXILIARES (KPIs e Eventos)
    # ========================================================
    path('api/coordenacao/kpis/', api_coordenacao_kpis, name='api_coordenacao_kpis'),
    path('api/coordenacao/desempenho/', api_coordenacao_desempenho, name='api_coordenacao_desempenho'),
    path('api/coordenacao/aprovacao/', api_coordenacao_aprovacao, name='api_coordenacao_aprovacao'),
    path('api/coordenacao/atividades/', api_coordenacao_atividades, name='api_coordenacao_atividades'),

    path('api/avisos/criar/', criar_aviso, name='criar_aviso'),
    path('api/eventos/criar/', criar_evento, name='criar_evento'),
    path('api/avisos-eventos/', api_avisos_eventos, name='api_avisos_eventos'),
]