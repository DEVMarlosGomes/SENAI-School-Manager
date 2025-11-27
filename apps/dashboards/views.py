import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from apps.academico.models import (
    Turma, Aluno, Professor, Secretaria, Coordenacao, 
    Historico, Curso, TurmaDisciplinaProfessor, Disciplina
)
from apps.usuarios.models import Profile
from .models import Material


# --- FUNÇÕES AUXILIARES DE PERMISSÃO ---

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
            if isaluno(request.user): userroles.append("aluno")
            if isprofessor(request.user): userroles.append("professor")
            if issecretaria(request.user): userroles.append("secretaria")
            if iscoordenacao(request.user): userroles.append("coordenacao")
            
            if not any(role in userroles for role in roles):
                messages.error(request, "Acesso negado a esta área.")
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# --- VIEW PRINCIPAL (ROTEAMENTO) ---

@login_required
def home(request):
    if isaluno(request.user): return redirect('aluno_dashboard')
    elif isprofessor(request.user): return redirect('professor_dashboard')
    elif issecretaria(request.user): return redirect('secretaria_dashboard')
    elif iscoordenacao(request.user): return redirect('coordenacao_dashboard')
    return render(request, "home.html")


# --- VIEWS ESPECÍFICAS DE PERFIL ---

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
    
    context.update({
        'total_alunos': Aluno.objects.count(),
        'total_turmas': Turma.objects.count(),
        'total_cursos': Curso.objects.count(),
    })
    return render(request, "dashboards/secretaria_dashboard.html", context)


# =============================================================================
# VISÃO GERAL DA COORDENAÇÃO (DASHBOARD PRINCIPAL)
# =============================================================================

@rolerequired("coordenacao")
def coordenacao_dashboard_view(request):
    context = {}
    
    # 1. Recuperar Coordenação
    try:
        coordenacao = Coordenacao.objects.select_related('user').get(user=request.user)
        context['coordenacao'] = coordenacao
    except Coordenacao.DoesNotExist:
        context['coordenacao'] = None
    
    # 2. KPIs Gerais
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.filter(status_professor='Ativo').count()
    total_turmas = Turma.objects.count()
    
    alunos_risco_count = Historico.objects.filter(
        Q(media_final__lt=6.0) | Q(frequencia_percentual__lt=75.0)
    ).values('id_aluno').distinct().count()

    # 3. GRÁFICO 1: DISPERSÃO (SCATTER PLOT)
    alunos_qs = Aluno.objects.annotate(
        media_geral=Avg('historico__media_final'),
        freq_geral=Avg('historico__frequencia_percentual')
    ).filter(media_geral__isnull=False)

    scatter_bom, scatter_atencao, scatter_risco = [], [], []

    for aluno in alunos_qs:
        nome = aluno.user.get_full_name()
        if len(nome) > 20: 
            nome = nome.split()[0] + " " + nome.split()[-1]
            
        nota = round(aluno.media_geral, 1)
        freq = round(aluno.freq_geral, 1)
        point = {'x': freq, 'y': nota, 'aluno': nome}

        if nota < 6.0 or freq < 75.0:
            scatter_risco.append(point)
        elif nota < 7.5:
            scatter_atencao.append(point)
        else:
            scatter_bom.append(point)

    # 4. GRÁFICO 2: EFICIÊNCIA POR CURSO (BARRAS)
    cursos = Curso.objects.all()
    labels_cursos, data_aprov, data_recup, data_reprov = [], [], [], []

    for curso in cursos:
        alunos_do_curso = Aluno.objects.filter(turma_atual__id_curso=curso).prefetch_related('historico')
        c_apr, c_rec, c_rep, has_data = 0, 0, 0, False

        for aluno in alunos_do_curso:
            historicos = list(aluno.historico.all())
            if not historicos: continue
            
            has_data = True
            status_list = [h.status_aprovacao.lower() for h in historicos if h.status_aprovacao]
            
            if any('reprovado' in s for s in status_list): c_rep += 1
            elif any('recuperação' in s or 'exame' in s for s in status_list): c_rec += 1
            else: c_apr += 1
        
        if has_data:
            nome_display = curso.cod_curso if len(curso.nome_curso) > 15 else curso.nome_curso
            labels_cursos.append(nome_display)
            data_aprov.append(c_apr)
            data_recup.append(c_rec)
            data_reprov.append(c_rep)

    # 5. Atividades Recentes
    recentes_qs = Aluno.objects.select_related('user').order_by('-data_matricula')[:5]
    atividades_recentes = [{
        'texto': f"Nova matrícula: {a.user.get_full_name()}",
        'data': a.data_matricula.strftime('%d/%m/%Y'),
    } for a in recentes_qs]

    dashboard_data = {
        'scatter_data': {'bom': scatter_bom, 'atencao': scatter_atencao, 'risco': scatter_risco},
        'grafico_comparativo': {
            'labels': labels_cursos,
            'aprovados': data_aprov,
            'recuperacao': data_recup,
            'reprovados': data_reprov
        }
    }

    context.update({
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
        'alunos_risco': alunos_risco_count,
        'atividades_recentes': atividades_recentes,
        'dashboard_data_json': json.dumps(dashboard_data)
    })
    
    return render(request, "dashboards/coordenacao_dashboard.html", context)


# =============================================================================
# PÁGINA DE DESEMPENHO ACADÊMICO
# =============================================================================

@rolerequired("coordenacao")
def coordenacao_desempenho_view(request):
    context = {}
    try:
        coordenacao = Coordenacao.objects.select_related('user').get(user=request.user)
        context['coordenacao'] = coordenacao
    except Coordenacao.DoesNotExist:
        context['coordenacao'] = None

    alunos_qs = Aluno.objects.select_related('turma_atual').prefetch_related('historico')
    alunos_list = []
    dist_notas = {'Aprovado': 0, 'Recuperação': 0, 'Reprovado': 0}

    for aluno in alunos_qs:
        historicos = list(aluno.historico.all())
        if not historicos:
            media, freq, situacao = 0, 0, "Sem notas"
        else:
            soma_notas = sum(h.media_final for h in historicos if h.media_final is not None)
            soma_freq = sum(h.frequencia_percentual for h in historicos if h.frequencia_percentual is not None)
            qtd = len(historicos)
            media = round(soma_notas / qtd, 1) if qtd > 0 else 0
            freq = round(soma_freq / qtd, 0) if qtd > 0 else 0
            
            if media < 5.0:
                situacao = "Reprovado"
                dist_notas['Reprovado'] += 1
            elif media < 7.0:
                situacao = "Recuperação"
                dist_notas['Recuperação'] += 1
            else:
                if freq >= 75:
                    situacao = "Aprovado"
                    dist_notas['Aprovado'] += 1
                else:
                    situacao = "Reprovado por Faltas"
                    dist_notas['Reprovado'] += 1

        alunos_list.append({
            'id': aluno.pk,
            'nome': aluno.user.get_full_name(),
            'matricula': aluno.RA_aluno,
            'turma': aluno.turma_atual.nome if aluno.turma_atual else 'Sem Turma',
            'media': media,
            'frequencia': freq,
            'situacao': situacao
        })

    turmas_qs = Turma.objects.all().annotate(qtd_alunos=Count('alunos'))
    turmas_list, freq_labels, freq_data = [], [], []

    for turma in turmas_qs:
        dados = Historico.objects.filter(turma_disciplina_professor__turma=turma).aggregate(
            media_geral=Avg('media_final'), freq_geral=Avg('frequencia_percentual')
        )
        m_geral = round(dados['media_geral'] or 0, 1)
        f_geral = round(dados['freq_geral'] or 0, 1)

        turmas_list.append({
            'id': turma.pk,
            'codigo': turma.nome, 
            'nome': turma.id_curso.nome_curso if turma.id_curso else "Curso N/A",
            'alunos': turma.qtd_alunos,
            'media_geral': m_geral
        })

        if turma.qtd_alunos > 0:
            freq_labels.append(turma.nome)
            freq_data.append(f_geral)

    desempenho_data = {
        'alunos': alunos_list,
        'turmas': turmas_list,
        'grafico_notas': dist_notas,
        'grafico_frequencia': {'labels': freq_labels, 'data': freq_data}
    }
    context['desempenho_data_json'] = json.dumps(desempenho_data)
    return render(request, "dashboards/coordenacao_desempenho.html", context)


# =============================================================================
# PÁGINA DE GESTÃO (CRUD)
# =============================================================================

@rolerequired("coordenacao")
def coordenacao_gestao_view(request):
    # 1. Busca Alunos
    alunos_list = [{
        'id': a.pk,
        'nome': a.user.get_full_name(),
        'matricula': a.RA_aluno,
        'turma': a.turma_atual.nome if a.turma_atual else 'Sem turma',
        'status': a.status_matricula
    } for a in Aluno.objects.select_related('user', 'turma_atual').all()]

    # 2. Busca Turmas
    turmas_qs = Turma.objects.select_related('id_curso').annotate(num_matriculados=Count('alunos'))
    turmas_list = []
    for t in turmas_qs:
        profs = TurmaDisciplinaProfessor.objects.filter(turma=t).values_list('professor__user__first_name', flat=True).distinct()
        prof_name = profs[0] if profs else "A definir"
        if len(profs) > 1: prof_name = "Vários"
        
        turmas_list.append({
            'id': t.pk, 'codigo': t.nome, 'nome': t.id_curso.nome_curso,
            'professor': prof_name, 'vagas': t.capacidade_maxima, 'matriculados': t.num_matriculados
        })

    # 3. Busca Professores
    profs_list = []
    for p in Professor.objects.select_related('user').all():
        num_turmas = TurmaDisciplinaProfessor.objects.filter(professor=p).values('turma').distinct().count()
        discs = TurmaDisciplinaProfessor.objects.filter(professor=p).values_list('disciplina__nome', flat=True).distinct()
        discs_str = ", ".join(list(discs)[:2]) + ("..." if len(discs) > 2 else "")
        profs_list.append({
            'id': p.pk, 'nome': p.user.get_full_name(), 'email': p.user.email,
            'disciplinas': discs_str or "Nenhuma", 'turmas': num_turmas
        })

    # 4. Busca Disciplinas
    discs_list = []
    for d in Disciplina.objects.all():
        num_turmas = TurmaDisciplinaProfessor.objects.filter(disciplina=d).values('turma').distinct().count()
        discs_list.append({
            'id': d.pk, 'codigo': d.cod_disciplina, 'nome': d.nome,
            'cargaHoraria': d.carga_horaria or 0, 'turmas': num_turmas
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


# =============================================================================
# API VIEWS (SAVE / DELETE)
# =============================================================================

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

        parts = nome_completo.strip().split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        turma = None
        if turma_nome:
            turma = Turma.objects.filter(nome=turma_nome).first()

        if aluno_id:
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
            if User.objects.filter(username=matricula).exists():
                return JsonResponse({'success': False, 'message': 'Matrícula já existe.'})

            user = User.objects.create_user(username=matricula, password="123mudar", first_name=first_name, last_name=last_name)
            from datetime import date
            aluno = Aluno.objects.create(
                user=user, RA_aluno=matricula, RG_aluno=f"RG-{matricula}", 
                data_nascimento=date(2000, 1, 1), genero="Não informado",
                estado_civil="Solteiro", turma_atual=turma, status_matricula=status
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
        user.delete()
        return JsonResponse({'success': True, 'message': 'Aluno excluído com sucesso!'})
    except Aluno.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Aluno não encontrado.'}, status=404)


# =============================================================================
# OUTRAS VIEWS (SECRETARIA / ALUNO)
# =============================================================================

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
def api_coordenacao_kpis(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_desempenho(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_aprovacao(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_atividades(request): return JsonResponse({'status': 'ok'})