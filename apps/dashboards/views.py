import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods  # IMPORT QUE FALTAVA
from django.http import JsonResponse
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.contrib.auth.models import User
from apps.academico.models import (
    Turma, Aluno, Professor, Secretaria, Coordenacao, 
    Historico, Curso, TurmaDisciplinaProfessor, Disciplina
)
from apps.usuarios.models import Profile
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
    context = {}
    try:
        aluno = Aluno.objects.select_related('user', 'turma_atual').get(user=request.user)
        context['aluno'] = aluno
    except Aluno.DoesNotExist:
        context['aluno'] = None
    return render(request, "dashboards/aluno_dashboard.html", context)


@rolerequired("professor")
def professor_dashboard_view(request):
    context = {}
    try:
        professor = Professor.objects.select_related('user').get(user=request.user)
        context['professor'] = professor
    except Professor.DoesNotExist:
        context['professor'] = None
    return render(request, "dashboards/professor_dashboard.html", context)


@rolerequired("secretaria")
def secretaria_dashboard_view(request):
    context = {}
    try:
        secretaria = Secretaria.objects.select_related('user').get(user=request.user)
        context['secretaria'] = secretaria
    except Secretaria.DoesNotExist:
        context['secretaria'] = None
    
    total_alunos = Aluno.objects.count()
    total_turmas = Turma.objects.count()
    total_cursos = Curso.objects.count()
    
    context.update({
        'total_alunos': total_alunos,
        'total_turmas': total_turmas,
        'total_cursos': total_cursos,
    })
    return render(request, "dashboards/secretaria_dashboard.html", context)


@rolerequired("coordenacao")
def coordenacao_dashboard_view(request):
    context = {}
    try:
        coordenacao = Coordenacao.objects.select_related('user').get(user=request.user)
        context['coordenacao'] = coordenacao
    except Coordenacao.DoesNotExist:
        context['coordenacao'] = None
    
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    
    context.update({
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
    })
    return render(request, "dashboards/coordenacao_dashboard.html", context)


@rolerequired("coordenacao")
def coordenacao_desempenho_view(request):
    return render(request, "dashboards/coordenacao_desempenho.html")


@rolerequired("coordenacao")
def coordenacao_gestao_view(request):
    # 1. Busca Alunos Reais
    alunos_qs = Aluno.objects.select_related('user', 'turma_atual').all()
    alunos_list = []
    for a in alunos_qs:
        alunos_list.append({
            'id': a.pk,
            'nome': a.user.get_full_name(),
            'matricula': a.RA_aluno,
            'turma': a.turma_atual.nome if a.turma_atual else 'Sem turma',
            'status': a.status_matricula
        })

    # 2. Busca Turmas Reais
    turmas_qs = Turma.objects.select_related('id_curso').annotate(
        num_matriculados=Count('alunos')
    ).all()
    turmas_list = []
    for t in turmas_qs:
        profs = TurmaDisciplinaProfessor.objects.filter(turma=t).values_list('professor__user__first_name', flat=True).distinct()
        prof_name = profs[0] if profs else "A definir"
        if len(profs) > 1: prof_name = "Vários"
        
        turmas_list.append({
            'id': t.pk,
            'codigo': t.nome,
            'nome': t.id_curso.nome_curso,
            'professor': prof_name,
            'vagas': t.capacidade_maxima,
            'matriculados': t.num_matriculados
        })

    # 3. Busca Professores Reais
    prof_qs = Professor.objects.select_related('user').all()
    profs_list = []
    for p in prof_qs:
        num_turmas = TurmaDisciplinaProfessor.objects.filter(professor=p).values('turma').distinct().count()
        discs = TurmaDisciplinaProfessor.objects.filter(professor=p).values_list('disciplina__nome', flat=True).distinct()
        discs_str = ", ".join(list(discs)[:2]) + ("..." if len(discs) > 2 else "")

        profs_list.append({
            'id': p.pk,
            'nome': p.user.get_full_name(),
            'email': p.user.email,
            'disciplinas': discs_str or "Nenhuma",
            'turmas': num_turmas
        })

    # 4. Busca Disciplinas Reais
    disc_qs = Disciplina.objects.all()
    discs_list = []
    for d in disc_qs:
        num_turmas = TurmaDisciplinaProfessor.objects.filter(disciplina=d).values('turma').distinct().count()
        discs_list.append({
            'id': d.pk,
            'codigo': d.cod_disciplina,
            'nome': d.nome,
            'cargaHoraria': d.carga_horaria or 0,
            'turmas': num_turmas
        })

    context = {
        'alunos_json': json.dumps(alunos_list, cls=DjangoJSONEncoder),
        'turmas_json': json.dumps(turmas_list, cls=DjangoJSONEncoder),
        'professores_json': json.dumps(profs_list, cls=DjangoJSONEncoder),
        'disciplinas_json': json.dumps(discs_list, cls=DjangoJSONEncoder),
    }
    
    return render(request, "dashboards/coordenacao_gestao.html", context)


@rolerequired("coordenacao")
def coordenacao_comunicacao_view(request):
    return render(request, "dashboards/coordenacao_comunicacao.html")


@rolerequired("coordenacao")
def coordenacao_relatorios_view(request):
    return render(request, "dashboards/coordenacao_relatorios.html")


# --- API VIEWS PARA SALVAR E DELETAR ---

@require_http_methods(["POST"])
@rolerequired("coordenacao")
def save_aluno_view(request):
    try:
        data = json.loads(request.body)
        aluno_id = data.get('id')
        nome_completo = data.get('nome')
        matricula = data.get('matricula')
        turma_nome = data.get('turma')
        status = data.get('status')

        # Separa o nome para o User
        parts = nome_completo.strip().split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        # Busca a turma
        turma = None
        if turma_nome:
            turma = Turma.objects.filter(nome=turma_nome).first()

        if aluno_id:
            # EDITAR
            aluno = Aluno.objects.get(pk=aluno_id)
            user = aluno.user
            
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            aluno.RA_aluno = matricula
            aluno.turma_atual = turma
            aluno.status_matricula = status
            aluno.save()
            msg = "Aluno atualizado com sucesso!"
        else:
            # NOVO
            if User.objects.filter(username=matricula).exists():
                return JsonResponse({'success': False, 'message': 'Matrícula já existe como usuário.'})

            user = User.objects.create_user(username=matricula, password="123mudar", first_name=first_name, last_name=last_name)
            
            # Valores padrão para campos obrigatórios não enviados no form simples
            from datetime import date
            aluno = Aluno.objects.create(
                user=user,
                RA_aluno=matricula,
                RG_aluno=f"RG-{matricula}", 
                data_nascimento=date(2000, 1, 1),
                genero="Não informado",
                estado_civil="Solteiro",
                turma_atual=turma,
                status_matricula=status
            )
            Profile.objects.create(user=user, tipo='aluno')
            msg = "Aluno criado com sucesso!"

        return JsonResponse({'success': True, 'message': msg})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@require_http_methods(["DELETE", "POST"])
@rolerequired("coordenacao")
def delete_aluno_view(request, pk):
    try:
        aluno = Aluno.objects.get(pk=pk)
        user = aluno.user
        aluno.delete()
        user.delete() # Apaga o login também
        return JsonResponse({'success': True, 'message': 'Aluno excluído com sucesso!'})
    except Aluno.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Aluno não encontrado.'}, status=404)


# --- OUTRAS VIEWS ---

@rolerequired("secretaria")
def gestao_alunos_view(request):
    alunos = Aluno.objects.select_related('user', 'turma_atual').all()
    return render(request, "dashboards/gestao_alunos.html", {'alunos': alunos})

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

# APIs Placeholder
@login_required
def api_coordenacao_kpis(request):
    return JsonResponse({'status': 'ok'})

@login_required
def api_coordenacao_desempenho(request):
    return JsonResponse({'status': 'ok'})

@login_required
def api_coordenacao_aprovacao(request):
    return JsonResponse({'status': 'ok'})

@login_required
def api_coordenacao_atividades(request):
    return JsonResponse({'status': 'ok'})