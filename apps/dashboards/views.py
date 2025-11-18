from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.academico.models import (
    Turma, Aluno, Professor, Secretaria, Coordenacao, 
    Historico, Curso, TurmaDisciplinaProfessor
)
from .models import Material

def isaluno(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'aluno'

def isprofessor(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'professor'

def issecretaria(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'secretaria'

def iscoordenacao(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'coordenacao'

def rolerequired(*roles):
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            userroles = []
            if isaluno(request.user):
                userroles.append("aluno")
            if isprofessor(request.user):
                userroles.append("professor")
            if issecretaria(request.user):
                userroles.append("secretaria")
            if iscoordenacao(request.user):
                userroles.append("coordenacao")
            if not any(role in userroles for role in roles):
                messages.error(request, "Acesso negado a esta área.")
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
def home(request):
    if isaluno(request.user):
        return redirect('aluno_dashboard')
    elif isprofessor(request.user):
        return redirect('professor_dashboard')
    elif issecretaria(request.user):
        return redirect('secretaria_dashboard')
    elif iscoordenacao(request.user):
        return redirect('coordenacao_dashboard')
    return render(request, "home.html")

@rolerequired("aluno")
def aluno_dashboard_view(request):
    return render(request, "dashboards/aluno_dashboard.html")

@rolerequired("professor")
def professor_dashboard_view(request):
    return render(request, "dashboards/professor_dashboard.html")

@rolerequired("secretaria")
def secretaria_dashboard_view(request):
    return render(request, "dashboards/secretaria_dashboard.html")

@rolerequired("coordenacao")
def coordenacao_dashboard_view(request):
    return render(request, "dashboards/coordenacao_dashboard.html")

@rolerequired("coordenacao")
def coordenacao_desempenho_view(request):
    return render(request, "dashboards/coordenacao_desempenho.html")

@rolerequired("coordenacao")
def coordenacao_gestao_view(request):
    return render(request, "dashboards/coordenacao_gestao.html")

@rolerequired("coordenacao")
def coordenacao_comunicacao_view(request):
    return render(request, "dashboards/coordenacao_comunicacao.html")

@rolerequired("coordenacao")
def coordenacao_relatorios_view(request):
    return render(request, "dashboards/coordenacao_relatorios.html")

@rolerequired("secretaria")
def gestao_alunos_view(request):
    return render(request, "dashboards/gestao_alunos.html")

@rolerequired("secretaria")
def gestao_documentos_view(request):
    return render(request, "dashboards/gestao_documentos.html")

@rolerequired("secretaria")
def controle_financeiro_view(request):
    return render(request, "dashboards/controle_financeiro.html")

@rolerequired("secretaria")
def comunicacao_secretaria_view(request):
    return render(request, "dashboards/comunicacao_secretaria.html")

@login_required
def perfil_view(request):
    return render(request, "dashboards/perfil.html")

@rolerequired("aluno")
def materiais_estudo_view(request):
    return render(request, "dashboards/materiais_estudo.html")

@rolerequired("aluno")
def boletim_view(request):
    return render(request, "dashboards/boletim.html")

@rolerequired("aluno")
def calendario_view(request):
    return render(request, "dashboards/calendario.html")

@rolerequired("aluno")
def avisos_eventos_view(request):
    return render(request, "dashboards/avisos_eventos.html")

@login_required
def api_coordenacao_kpis(request):
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok'})

@login_required
def api_coordenacao_desempenho(request):
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok'})

@login_required
def api_coordenacao_aprovacao(request):
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok'})

@login_required
def api_coordenacao_atividades(request):
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok'})
