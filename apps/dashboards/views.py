import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Avg, Sum, Q
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django.urls import reverse

# Imports dos modelos
from apps.academico.models import (
    Turma, Aluno, Professor, Secretaria, Coordenacao, 
    Historico, Curso, TurmaDisciplinaProfessor, Disciplina
)
from apps.usuarios.models import Profile, PendingRegistration
from apps.payments.models import Pagamento
from apps.relatorios.models import DocumentoEmitido

# =============================================================================
# 1. DECORATORS E PERMISSÕES
# =============================================================================

def isaluno(user): return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'aluno'
def isprofessor(user): return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'professor'
def issecretaria(user): return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'secretaria'
def iscoordenacao(user): return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'coordenacao'

def rolerequired(*roles):
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            userroles = []
            if hasattr(request.user, 'profile'):
                userroles.append(request.user.profile.tipo)
            
            if request.user.is_superuser: return view_func(request, *args, **kwargs)

            if not any(role in userroles for role in roles):
                messages.error(request, "Acesso negado.")
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# =============================================================================
# 2. VIEW PRINCIPAL
# =============================================================================

@login_required
def home(request):
    if isaluno(request.user): return redirect('aluno_dashboard')
    elif isprofessor(request.user): return redirect('professor_dashboard')
    elif issecretaria(request.user): return redirect('secretaria_dashboard')
    elif iscoordenacao(request.user): return redirect('coordenacao_dashboard')
    return render(request, "home.html")

# =============================================================================
# 3. DASHBOARDS E GESTÃO
# =============================================================================

@rolerequired("secretaria", "coordenacao")
def gestao_documentos_view(request):
    """
    Lista histórico de documentos emitidos com busca.
    """
    documentos = DocumentoEmitido.objects.select_related(
        'aluno', 
        'aluno__user', 
        'solicitante'
    ).all().order_by('-data_emissao')
    
    search_query = request.GET.get('q')
    
    if search_query and search_query.strip() and search_query != 'None':
        documentos = documentos.filter(
            Q(aluno__user__first_name__icontains=search_query) |
            Q(aluno__user__last_name__icontains=search_query) |
            Q(aluno__RA_aluno__icontains=search_query) |
            Q(codigo_validacao__icontains=search_query)
        )
    else:
        search_query = ''
    
    documentos = documentos[:50]
    
    context = {
        'documentos': documentos,
        'search_query': search_query
    }
    return render(request, "dashboards/gestao_documentos.html", context)

@rolerequired("secretaria")
def secretaria_dashboard_view(request):
    context = {}
    try:
        secretaria = Secretaria.objects.select_related('user').get(user=request.user)
        context['secretaria'] = secretaria
    except Secretaria.DoesNotExist:
        context['secretaria'] = None
    
    total_alunos = Aluno.objects.count()
    matriculas_ativas = Aluno.objects.filter(status_matricula='Ativo').count()
    pgtos_pendentes = Pagamento.objects.filter(status='pendente').count()
    
    docs_recentes = DocumentoEmitido.objects.select_related('aluno__user').order_by('-data_emissao')[:5]

    context.update({
        'total_alunos': total_alunos,
        'total_turmas': Turma.objects.count(),
        'total_cursos': Curso.objects.count(),
        'matriculas_ativas': matriculas_ativas,
        'pgtos_pendentes': pgtos_pendentes,
        'docs_recentes': docs_recentes
    })
    return render(request, "dashboards/secretaria_dashboard.html", context)

@rolerequired("secretaria", "coordenacao")
def gestao_alunos_view(request):
    alunos_qs = Aluno.objects.select_related(
        'user', 
        'user__profile',
        'turma_atual',
        'turma_atual__id_curso'
    ).all().order_by('user__first_name')
    
    search_query = request.GET.get('q')
    filter_turma = request.GET.get('turma')
    filter_status = request.GET.get('status')

    if search_query and search_query != 'None':
        alunos_qs = alunos_qs.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(RA_aluno__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    if filter_turma and filter_turma != 'todas' and filter_turma != 'None':
        if filter_turma.isdigit():
            alunos_qs = alunos_qs.filter(turma_atual__id=filter_turma)
        
    if filter_status and filter_status != 'todos' and filter_status != 'None':
        alunos_qs = alunos_qs.filter(status_matricula=filter_status)

    total_alunos = alunos_qs.count()
    turmas_disponiveis = Turma.objects.all().order_by('nome')
    status_choices = ['Ativo', 'Trancado', 'Cancelado'] 

    paginator = Paginator(alunos_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    pode_editar = (request.user.profile.tipo == 'coordenacao')

    context = {
        'page_obj': page_obj,
        'search_query': search_query if search_query != 'None' else '',
        'filter_turma': filter_turma if filter_turma != 'None' else '', 
        'filter_status': filter_status if filter_status != 'None' else '',
        'total_alunos': total_alunos,
        'turmas': turmas_disponiveis,
        'status_choices': status_choices,
        'pode_editar': pode_editar
    }
    return render(request, "dashboards/gestao_alunos.html", context)


@rolerequired("professor")
def professor_dashboard_view(request):
    context = {}
    try:
        professor = Professor.objects.select_related('user').get(user=request.user)
        context['professor'] = professor
    except Professor.DoesNotExist:
        context['professor'] = None
        return render(request, "dashboards/professor_dashboard.html", context)

    alocacoes = TurmaDisciplinaProfessor.objects.filter(professor=professor).select_related('turma', 'disciplina')
    
    total_turmas = alocacoes.values('turma').distinct().count()
    turmas_ids = alocacoes.values_list('turma_id', flat=True)
    total_alunos = Aluno.objects.filter(turma_atual__id__in=turmas_ids).distinct().count()
    pendencias = Turma.objects.filter(id__in=turmas_ids, status_aprovacao='Pendente').count()

    historicos_alunos = Historico.objects.filter(
        turma_disciplina_professor__in=alocacoes
    ).select_related('id_aluno', 'id_aluno__user', 'turma_disciplina_professor__disciplina', 'turma_disciplina_professor__turma')

    alunos_risco_list = []
    distribuicao_notas = {'0-4': 0, '5-6': 0, '7-8': 0, '9-10': 0}

    for hist in historicos_alunos:
        motivo = []
        nota = float(hist.media_final) if hist.media_final is not None else 0.0
        freq = float(hist.frequencia_percentual) if hist.frequencia_percentual is not None else 0.0

        if nota < 5: distribuicao_notas['0-4'] += 1
        elif nota < 7: distribuicao_notas['5-6'] += 1
        elif nota < 9: distribuicao_notas['7-8'] += 1
        else: distribuicao_notas['9-10'] += 1

        if nota < 6.0:
            motivo.append(f"Nota: {nota}")
        if freq < 75.0:
            motivo.append(f"Freq: {freq:.0f}%")
        
        if motivo:
            alunos_risco_list.append({
                'nome': hist.id_aluno.user.get_full_name(),
                'disciplina': hist.turma_disciplina_professor.disciplina.nome,
                'motivo': ", ".join(motivo),
                'classe_css': 'text-danger fw-bold'
            })

    grafico_qs = historicos_alunos.values('turma_disciplina_professor__turma__nome').annotate(media=Avg('media_final'))
    
    chart_labels = [i['turma_disciplina_professor__turma__nome'] for i in grafico_qs]
    chart_data = [round(i['media'] or 0, 1) for i in grafico_qs]
    if not chart_labels: chart_labels, chart_data = ["Sem dados"], [0]

    dashboard_data = {
        'labels': chart_labels, 
        'data': chart_data,
        'distribuicao_notas': list(distribuicao_notas.values()),
        'labels_distribuicao': list(distribuicao_notas.keys())
    }

    context.update({
        'total_turmas': total_turmas,
        'total_alunos': total_alunos,
        'pendencias': pendencias,
        'dashboard_data_obj': dashboard_data,
        'turma_destaque': alocacoes.first().turma if alocacoes.exists() else None,
        'alocacoes': alocacoes,
        'alunos_risco': alunos_risco_list[:10]
    })
    return render(request, "dashboards/professor_dashboard.html", context)

@rolerequired("coordenacao")
def coordenacao_dashboard_view(request):
    context = {}
    try:
        coordenacao = Coordenacao.objects.select_related('user').get(user=request.user)
        context['coordenacao'] = coordenacao
    except Coordenacao.DoesNotExist:
        context['coordenacao'] = None
    
    total_alunos = Aluno.objects.count()
    total_alunos_ativos = Aluno.objects.filter(status_matricula='Ativo').count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    
    student_stats = Historico.objects.filter(id_aluno__status_matricula='Ativo').values('id_aluno').annotate(
        avg_media=Avg('media_final'),
        avg_freq=Avg('frequencia_percentual')
    )

    student_ids = [s['id_aluno'] for s in student_stats]
    alunos_objs = Aluno.objects.select_related('user').filter(user__id__in=student_ids)
    aluno_name_map = {a.user.id: a.user.get_full_name() for a in alunos_objs}

    scatter_data = {'bom': [], 'atencao': [], 'risco': []}
    risco_ids = set()

    for s in student_stats:
        aluno_id = s['id_aluno']
        media = float(s['avg_media'] or 0.0)
        freq = float(s['avg_freq'] or 0.0)
        ponto = {'x': round(freq, 1), 'y': round(media, 1), 'aluno': aluno_name_map.get(aluno_id, '')}

        if media >= 7.0 and freq >= 85.0:
            scatter_data['bom'].append(ponto)
        elif media < 5.0 or freq < 75.0:
            scatter_data['risco'].append(ponto)
            risco_ids.add(aluno_id)
        else:
            scatter_data['atencao'].append(ponto)

    atividades = [
        {'texto': 'Análise de desempenho global iniciada', 'data': 'Hoje'},
        {'texto': 'Conselho de classe agendado', 'data': 'Ontem'}
    ]

    count_risco = len(risco_ids)

    grafico_comparativo = {'labels': [], 'aprovados': [], 'recuperacao': [], 'reprovados': []}
    cursos = Curso.objects.all().order_by('nome_curso')
    for curso in cursos:
        grafico_comparativo['labels'].append(curso.nome_curso)
        alunos_no_curso = Aluno.objects.filter(turma_atual__id_curso=curso).select_related('user')
        alunos_ids = [a.user.id for a in alunos_no_curso]
        if not alunos_ids:
            grafico_comparativo['aprovados'].append(0)
            grafico_comparativo['recuperacao'].append(0)
            grafico_comparativo['reprovados'].append(0)
            continue

        stats = Historico.objects.filter(id_aluno__user__id__in=alunos_ids).values('id_aluno').annotate(avg_media=Avg('media_final'))
        apro=rec=rep=0
        for st in stats:
            m = float(st['avg_media'] or 0)
            if m >= 7.0:
                apro += 1
            elif m >= 5.0:
                rec += 1
            else:
                rep += 1

        grafico_comparativo['aprovados'].append(apro)
        grafico_comparativo['recuperacao'].append(rec)
        grafico_comparativo['reprovados'].append(rep)

    context.update({
        'total_alunos': total_alunos,
        'total_alunos_ativos': total_alunos_ativos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
        'alunos_risco_count': count_risco,
        'alunos_risco_pct': int((count_risco / total_alunos_ativos * 100) if total_alunos_ativos > 0 else 0),
        'dashboard_data_json': json.dumps({'scatter_data': scatter_data, 'grafico_comparativo': grafico_comparativo}, cls=DjangoJSONEncoder),
        'atividades_recentes': atividades
    })
    return render(request, "dashboards/coordenacao_dashboard.html", context)

@rolerequired("coordenacao")
def coordenacao_gestao_view(request):
    alunos_qs = Aluno.objects.select_related('user', 'turma_atual').all().order_by('user__first_name')
    alunos_json = []
    for a in alunos_qs:
        edit_url = reverse('admin:academico_aluno_change', args=[a.user.id])
        alunos_json.append({
            'id': a.user.id,
            'nome': a.user.get_full_name(),
            'matricula': getattr(a, 'RA_aluno', ''),
            'turma': a.turma_atual.nome if getattr(a, 'turma_atual', None) else '-',
            'status': getattr(a, 'status_matricula', ''),
            'edit_url': edit_url
        })

    turmas_qs = Turma.objects.select_related('id_curso').all().order_by('nome')
    turmas_json = []
    for t in turmas_qs:
        edit_url = reverse('admin:academico_turma_change', args=[t.id])
        turmas_json.append({
            'id': t.id,
            'codigo': t.nome,
            'nome': t.id_curso.nome_curso if getattr(t, 'id_curso', None) else t.nome,
            'professor': '',
            'matriculados': t.alunos.count(),
            'vagas': t.capacidade_maxima,
            'edit_url': edit_url
        })

    prof_qs = Professor.objects.select_related('user').all().order_by('user__first_name')
    professores_json = []
    for p in prof_qs:
        edit_url = reverse('admin:academico_professor_change', args=[p.user.id])
        turmas_count = TurmaDisciplinaProfessor.objects.filter(professor=p).values('turma').distinct().count()
        professores_json.append({
            'id': p.user.id,
            'nome': p.user.get_full_name(),
            'email': p.user.email,
            'turmas': turmas_count,
            'edit_url': edit_url
        })

    disc_qs = Disciplina.objects.all().order_by('cod_disciplina')
    disciplinas_json = []
    for d in disc_qs:
        edit_url = reverse('admin:academico_disciplina_change', args=[d.id])
        disciplinas_json.append({
            'id': d.id,
            'codigo': d.cod_disciplina,
            'nome': d.nome,
            'cargaHoraria': d.carga_horaria or 0,
            'edit_url': edit_url
        })

    context = {
        'alunos_json': json.dumps(alunos_json, cls=DjangoJSONEncoder),
        'turmas_json': json.dumps(turmas_json, cls=DjangoJSONEncoder),
        'professores_json': json.dumps(professores_json, cls=DjangoJSONEncoder),
        'disciplinas_json': json.dumps(disciplinas_json, cls=DjangoJSONEncoder),
        'url_novo_aluno': reverse('admin:academico_aluno_add'),
        'url_nova_turma': reverse('admin:academico_turma_add'),
        'url_novo_professor': reverse('admin:academico_professor_add'),
        'url_nova_disciplina': reverse('admin:academico_disciplina_add'),
    }
    return render(request, "dashboards/coordenacao_gestao.html", context)

@rolerequired("coordenacao")
def coordenacao_aprovacao_view(request):
    pendentes = PendingRegistration.objects.filter(status='pendente').order_by('-data_solicitacao')
    historico = PendingRegistration.objects.exclude(status='pendente').order_by('-data_aprovacao')[:10]
    return render(request, "dashboards/coordenacao_aprovacao.html", {
        'pendentes': pendentes,
        'historico': historico
    })

@require_http_methods(["POST"])
@rolerequired("coordenacao")
def aprovar_registro(request, pk):
    registro = get_object_or_404(PendingRegistration, pk=pk)
    try:
        user = registro.aprovar(admin_user=request.user)
        if registro.tipo_solicitado == 'aluno':
            import random
            ra_temp = f"RA{date.today().year}{random.randint(1000,9999)}"
            Aluno.objects.create(
                user=user,
                RA_aluno=ra_temp, 
                RG_aluno=f"TEMP-{user.id}",
                data_nascimento=date(2000, 1, 1),
                genero='Não informado',
                estado_civil='Solteiro'
            )
        messages.success(request, f"Usuário {registro.primeiro_nome} aprovado com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao aprovar: {str(e)}")
    return redirect('coordenacao_aprovacao')

@require_http_methods(["POST"])
@rolerequired("coordenacao")
def rejeitar_registro(request, pk):
    registro = get_object_or_404(PendingRegistration, pk=pk)
    motivo = request.POST.get('motivo', 'Rejeitado pela coordenação')
    try:
        registro.rejeitar(admin_user=request.user, motivo=motivo)
        messages.warning(request, f"Solicitação de {registro.primeiro_nome} foi rejeitada.")
    except Exception as e:
        messages.error(request, f"Erro ao rejeitar: {str(e)}")
    return redirect('coordenacao_aprovacao')

@rolerequired("aluno")
def boletim_view(request):
    try:
        aluno = Aluno.objects.select_related('user', 'turma_atual', 'turma_atual__id_curso').get(user=request.user)
    except Aluno.DoesNotExist:
        messages.error(request, "Perfil de aluno não encontrado.")
        return redirect('home')

    historico_qs = Historico.objects.filter(id_aluno=aluno).select_related(
        'turma_disciplina_professor',
        'turma_disciplina_professor__disciplina',
        'turma_disciplina_professor__professor',
        'turma_disciplina_professor__turma'
    ).order_by('turma_disciplina_professor__turma__ano_letivo', 'turma_disciplina_professor__disciplina__nome')

    periodos = sorted(list(set(h.periodo_realizacao for h in historico_qs)), reverse=True)
    dados_agrupados = []
    
    for periodo in periodos:
        disciplinas_periodo = historico_qs.filter(periodo_realizacao=periodo)
        media_periodo = disciplinas_periodo.aggregate(m=Avg('media_final'))['m'] or 0
        itens = []
        for h in disciplinas_periodo:
            status = h.status_aprovacao or 'Cursando'
            cor_status = 'secondary'
            if status == 'Aprovado': cor_status = 'success'
            elif status == 'Reprovado': cor_status = 'danger'
            elif status == 'Recuperação': cor_status = 'warning'
            elif status == 'Cursando': cor_status = 'info'

            itens.append({
                'disciplina': h.turma_disciplina_professor.disciplina.nome,
                'professor': h.turma_disciplina_professor.professor.user.get_full_name() if h.turma_disciplina_professor.professor else 'A definir',
                'nota': h.media_final,
                'faltas': h.total_faltas,
                'frequencia': h.frequencia_percentual,
                'status': status,
                'cor_status': cor_status,
                'carga_horaria': h.turma_disciplina_professor.disciplina.carga_horaria
            })
        dados_agrupados.append({
            'periodo': periodo,
            'media_geral': round(media_periodo, 1),
            'disciplinas': itens
        })

    context = {
        'aluno': aluno,
        'boletim_agrupado': dados_agrupados,
        'data_hoje': date.today()
    }
    return render(request, "dashboards/boletim.html", context)


@login_required
def perfil_view(request):
    user = request.user
    context = {'user': user}
    if hasattr(user, 'profile'):
        context['profile'] = user.profile
        if user.profile.tipo == 'aluno' and hasattr(user, 'aluno'):
            context['dados_academicos'] = user.aluno
        elif user.profile.tipo == 'professor' and hasattr(user, 'professor'):
            context['dados_academicos'] = user.professor
    return render(request, "dashboards/perfil.html", context)

@rolerequired("secretaria")
def controle_financeiro_view(request):
    pagamentos = Pagamento.objects.select_related('aluno').all().order_by('-data_criacao')
    recebido = pagamentos.filter(status='pago').aggregate(total=Sum('valor'))['total'] or 0
    pendente = pagamentos.filter(status='pendente').aggregate(total=Sum('valor'))['total'] or 0
    total_geral = recebido + pendente
    kpi_inadimplencia = (pendente / total_geral * 100) if total_geral > 0 else 0

    context = {
        'pagamentos': pagamentos,
        'kpi_recebido': recebido,
        'kpi_pendente': pendente,
        'kpi_inadimplencia': round(kpi_inadimplencia, 1),
        'alunos_para_select': Aluno.objects.select_related('user').all()
    }
    return render(request, "dashboards/controle_financeiro.html", context)

@rolerequired("aluno")
def aluno_financeiro_view(request):
    pagamentos = Pagamento.objects.filter(aluno=request.user).order_by('-data_criacao')
    total = sum(p.valor for p in pagamentos.filter(status='pendente'))
    context = {'pagamentos': pagamentos, 'total_pendente': total}
    return render(request, "dashboards/aluno_financeiro.html", context)

@rolerequired("aluno")
def aluno_dashboard_view(request):
    context = {}
    try:
        aluno = Aluno.objects.select_related('user', 'turma_atual').get(user=request.user)
        context['aluno'] = aluno
    except Aluno.DoesNotExist:
        context['aluno'] = None
        context['dashboard_data_json'] = json.dumps({'labels': [], 'data': []})
        return render(request, "dashboards/aluno_dashboard.html", context)

    historico = aluno.historico.all().select_related(
        'turma_disciplina_professor',
        'turma_disciplina_professor__disciplina'
    )
    
    media_geral = historico.aggregate(Avg('media_final'))['media_final__avg'] or 0
    total_faltas = historico.aggregate(Sum('total_faltas'))['total_faltas__sum'] or 0
    
    minhas_notas = []
    chart_labels = []
    chart_data = []

    for h in historico:
        nota = float(h.media_final) if h.media_final is not None else 0.0
        try:
            disciplina_nome = h.turma_disciplina_professor.disciplina.nome
        except AttributeError:
            disciplina_nome = "Disciplina S/N"
        
        chart_labels.append(disciplina_nome)
        chart_data.append(round(nota, 1))

        cor = 'success'
        if nota < 6.0: cor = 'danger'
        elif nota < 7.0: cor = 'warning'
        
        prof_nome = 'N/A'
        try:
            if h.turma_disciplina_professor.professor:
                prof_nome = h.turma_disciplina_professor.professor.user.get_full_name()
        except AttributeError:
            pass
        
        minhas_notas.append({
            'disciplina': disciplina_nome,
            'professor': prof_nome,
            'nota': nota,
            'cor': cor
        })

    dashboard_data = {'labels': chart_labels, 'data': chart_data}
    pendencias_fin = Pagamento.objects.filter(aluno=request.user, status='pendente').exists()
    status_financeiro = "Pendente" if pendencias_fin else "Em Dia"
    cor_financeiro = "warning" if pendencias_fin else "success"

    context.update({
        'media_geral': round(media_geral, 1),
        'total_faltas': total_faltas,
        'minhas_notas': minhas_notas,
        'status_financeiro': status_financeiro,
        'cor_financeiro': cor_financeiro,
        'dashboard_data_json': dashboard_data
    })
    return render(request, "dashboards/aluno_dashboard.html", context)

@login_required
@require_http_methods(["POST"])
def api_salvar_diario(request):
    try:
        data = json.loads(request.body)
        historico_id = data.get('historico_id')
        campo = data.get('campo')
        valor = data.get('valor')

        historico = get_object_or_404(Historico, id=historico_id)
        
        if historico.turma_disciplina_professor.professor.user != request.user:
            return JsonResponse({'success': False, 'error': 'Acesso negado. Você não é o professor desta turma.'}, status=403)

        if campo == 'nota':
            val_float = float(valor)
            if val_float < 0 or val_float > 10:
                return JsonResponse({'success': False, 'error': 'Nota deve ser entre 0 e 10.'}, status=400)
            historico.nota_final = val_float
            historico.media_final = val_float
        elif campo == 'faltas':
            val_int = int(valor)
            if val_int < 0:
                return JsonResponse({'success': False, 'error': 'Faltas não podem ser negativas.'}, status=400)
            historico.total_faltas = val_int
        
        carga_horaria = historico.turma_disciplina_professor.disciplina.carga_horaria or 60
        faltas = historico.total_faltas or 0
        
        freq = ((carga_horaria - faltas) / carga_horaria) * 100
        historico.frequencia_percentual = round(freq, 1)

        nota = historico.nota_final or 0
        if freq < 75:
            historico.status_aprovacao = 'Reprovado por Faltas'
        elif nota >= 6.0:
            historico.status_aprovacao = 'Aprovado'
        elif nota >= 4.0:
            historico.status_aprovacao = 'Recuperação'
        else:
            historico.status_aprovacao = 'Reprovado'

        historico.save()
        
        return JsonResponse({
            'success': True, 
            'status': historico.status_aprovacao,
            'frequencia': historico.frequencia_percentual
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# Placeholder APIs
@login_required
def api_coordenacao_kpis(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_desempenho(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_aprovacao(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_atividades(request): return JsonResponse({'status': 'ok'})
@require_http_methods(["POST"])
@login_required 
def save_aluno_view(request): return JsonResponse({'success': True})
@require_http_methods(["DELETE", "POST"])
@login_required
def delete_aluno_view(request, pk): 
    try:
        aluno = get_object_or_404(Aluno, pk=pk)
        user = aluno.user
        user.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# Views necessárias para não quebrar urls
def coordenacao_desempenho_view(request): return render(request, "dashboards/coordenacao_desempenho.html")
def coordenacao_comunicacao_view(request): return render(request, "dashboards/coordenacao_comunicacao.html")
def coordenacao_relatorios_view(request): return render(request, "dashboards/coordenacao_relatorios.html")
def comunicacao_secretaria_view(request): return render(request, "dashboards/comunicacao_secretaria.html")