# apps/dashboards/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

@login_required
def aluno_dashboard_view(request):
    # Lógica para obter dados do aluno logado
    return render(request, 'dashboards/aluno_dashboard.html')

@login_required
def professor_dashboard_view(request):
    # Lógica de obtenção de dados do professor
    context = {
        'turmas_ativas': 4,
        'pendencias': 7,
        'proxima_aula': '15:30',
        'total_alunos': 127,
        'turma_destaque': {
            'nome': 'EI-2023A - Eletrotécnica Industrial',
            'alunos_matriculados': 32,
            'frequencia_media': 87,
            'nota_media': 8.2,
        },
        'alunos_em_risco': [
            {'nome': 'Maria Santos', 'motivo': 'Frequência: 69%', 'cor': 'danger'},
            {'nome': 'Joana Oliveira', 'motivo': 'Nota: 5.8', 'cor': 'warning'},
            {'nome': 'Ana Costa', 'motivo': 'Múltiplas faltas', 'cor': 'danger'},
        ],
    }
    return render(request, 'dashboards/professor_dashboard.html', context)


@login_required
def secretaria_dashboard_view(request):
    # Lógica de obtenção de dados do secretaria
    return render(request, 'dashboards/secretaria_dashboard.html')

@login_required
def coordenacao_dashboard_view(request):
    # Lógica de obtenção de dados do coordenador
    return render(request, 'dashboards/coordenacao_dashboard.html')

# Views placeholders para links que aparecem na sidebar/templates
def gestao_alunos_view(request):
    return render(request, 'not_implemented.html', {'title': 'Gestão de Alunos'})

def controle_financeiro_view(request):
    return render(request, 'not_implemented.html', {'title': 'Controle Financeiro'})

def gestao_documentos_view(request):
    return render(request, 'not_implemented.html', {'title': 'Gestão de Documentos'})

def comunicacao_secretaria_view(request):
    return render(request, 'not_implemented.html', {'title': 'Comunicação - Secretaria'})

def perfil_view(request):
    return render(request, 'not_implemented.html', {'title': 'Meu Perfil'})