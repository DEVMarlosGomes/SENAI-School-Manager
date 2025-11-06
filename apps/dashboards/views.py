from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.academico.models import Turma, Aluno, Matricula, Nota, Frequencia

def home(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            if request.user.profile.is_aluno:
                return redirect('aluno_dashboard')
            elif request.user.profile.is_professor:
                return redirect('professor_dashboard')
            elif request.user.profile.is_secretaria:
                return redirect('secretaria_dashboard')
            elif request.user.profile.is_coordenacao:
                return redirect('coordenacao_dashboard')
    return render(request, 'home.html')

@login_required
def aluno_dashboard_view(request):
    context = {
        'titulo': 'Dashboard do Aluno',
        'notas_recentes': Nota.objects.filter(matricula__aluno__user=request.user).order_by('-data')[:5],
        'faltas_recentes': Frequencia.objects.filter(matricula__aluno__user=request.user, presenca=False).order_by('-data')[:5]
    }
    return render(request, 'dashboards/aluno_dashboard.html', context)

@login_required
def professor_dashboard_view(request):
    context = {
        'titulo': 'Dashboard do Professor',
        'turmas_ativas': Turma.objects.filter(professor=request.user, ativa=True).count(),
        'total_alunos': Matricula.objects.filter(turma__professor=request.user, status='ativa').count(),
        'proximas_aulas': Turma.objects.filter(professor=request.user, ativa=True)[:5]
    }
    return render(request, 'dashboards/professor_dashboard.html', context)

@login_required
def secretaria_dashboard_view(request):
    context = {
        'titulo': 'Dashboard da Secretaria',
        'total_alunos': Aluno.objects.count(),
        'matriculas_ativas': Matricula.objects.filter(status='ativa').count(),
        'turmas_ativas': Turma.objects.filter(ativa=True).count()
    }
    return render(request, 'dashboards/secretaria_dashboard.html', context)

@login_required
def coordenacao_dashboard_view(request):
    context = {
        'titulo': 'Dashboard da Coordenação',
        'total_turmas': Turma.objects.count(),
        'total_alunos': Aluno.objects.count(),
        'total_professores': Turma.objects.values('professor').distinct().count()
    }
    return render(request, 'dashboards/coordenacao_dashboard.html', context)

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