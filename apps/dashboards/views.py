import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Avg, Count, Q, Sum
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django.core.paginator import Paginator

# Imports dos modelos
from apps.academico.models import (
    Turma, Aluno, Professor, Secretaria, Coordenacao, 
    Historico, Curso, TurmaDisciplinaProfessor, Disciplina
)
from apps.usuarios.models import Profile
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
            if isaluno(request.user): userroles.append("aluno")
            if isprofessor(request.user): userroles.append("professor")
            if issecretaria(request.user): userroles.append("secretaria")
            if iscoordenacao(request.user): userroles.append("coordenacao")
            
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
def gestao_alunos_view(request):
    """
    Lista de alunos com busca, filtros avançados e paginação.
    """
    alunos_qs = Aluno.objects.select_related(
        'user', 
        'user__profile',
        'turma_atual',
        'turma_atual__id_curso'
    ).all().order_by('user__first_name')
    
    search_query = request.GET.get('q')
    filter_turma = request.GET.get('turma')
    filter_status = request.GET.get('status')

    if search_query:
        alunos_qs = alunos_qs.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(RA_aluno__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    if filter_turma and filter_turma != 'todas':
        alunos_qs = alunos_qs.filter(turma_atual__id=filter_turma)
        
    if filter_status and filter_status != 'todos':
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
        'search_query': search_query,
        'filter_turma': filter_turma, 
        'filter_status': filter_status,
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

    # Busca Históricos para identificar alunos em risco
    historicos_alunos = Historico.objects.filter(
        turma_disciplina_professor__in=alocacoes
    ).select_related('id_aluno', 'id_aluno__user', 'turma_disciplina_professor__disciplina', 'turma_disciplina_professor__turma')

    alunos_risco_list = []
    for hist in historicos_alunos:
        motivo = []
        nota = float(hist.media_final) if hist.media_final is not None else 0.0
        freq = float(hist.frequencia_percentual) if hist.frequencia_percentual is not None else 0.0

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

    dashboard_data = {'labels': chart_labels, 'data': chart_data}

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
        'matriculas_ativas': Aluno.objects.filter(status_matricula='Ativo').count()
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
    
    # 1. Recuperar KPIs
    total_alunos = Aluno.objects.count()
    # Considerar apenas alunos com matrícula ativa para métricas de risco/performace
    total_alunos_ativos = Aluno.objects.filter(status_matricula='Ativo').count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    # 2. Calcular Dados para o Gráfico de Dispersão (Desempenho x Frequência)
    # Vamos agregar por aluno (evitar contagem duplicada quando houver múltiplos históricos)
    # Agregar históricos somente para alunos ativos
    student_stats = Historico.objects.filter(id_aluno__status_matricula='Ativo').values('id_aluno').annotate(
        avg_media=Avg('media_final'),
        avg_freq=Avg('frequencia_percentual')
    )

    # Buscar nomes dos alunos em batch
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

    # 3. Atividades Recentes (Placeholder ou Logs Reais)
    atividades = [
        {'texto': 'Análise de desempenho global iniciada', 'data': 'Hoje'},
        {'texto': 'Conselho de classe agendado', 'data': 'Ontem'}
    ]

    count_risco = len(risco_ids)

    # 3. Eficiência por Curso (Aprovados / Recuperação / Reprovados)
    grafico_comparativo = {'labels': [], 'aprovados': [], 'recuperacao': [], 'reprovados': []}
    cursos = Curso.objects.all().order_by('nome_curso')
    for curso in cursos:
        grafico_comparativo['labels'].append(curso.nome_curso)
        # Alunos atualmente neste curso (pelo campo turma_atual)
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
        # usa apenas alunos ativos como denominador para o percentual de risco
        'alunos_risco_pct': int((count_risco / total_alunos_ativos * 100) if total_alunos_ativos > 0 else 0),
        'dashboard_data_json': json.dumps({'scatter_data': scatter_data, 'grafico_comparativo': grafico_comparativo}, cls=DjangoJSONEncoder),
        'atividades_recentes': atividades
    })
    return render(request, "dashboards/coordenacao_dashboard.html", context)

@rolerequired("aluno")
def aluno_dashboard_view(request):
    context = {}
    
    # 1. Recupera o Aluno Logado
    try:
        # Usa o ID do usuário logado para encontrar o aluno correspondente
        aluno = Aluno.objects.select_related('user', 'turma_atual').get(user=request.user)
        context['aluno'] = aluno
    except Aluno.DoesNotExist:
        context['aluno'] = None
        context['dashboard_data_json'] = json.dumps({'labels': [], 'data': []})
        return render(request, "dashboards/aluno_dashboard.html", context)

    # 2. Busca Histórico usando o relacionamento reverso (Mais seguro contra nomes de FK)
    # Acessa todos os históricos vinculados a este aluno
    historico = aluno.historico.all().select_related(
        'turma_disciplina_professor',
        'turma_disciplina_professor__disciplina'
    )
    
    media_geral = historico.aggregate(Avg('media_final'))['media_final__avg'] or 0
    total_faltas = historico.aggregate(Sum('total_faltas'))['total_faltas__sum'] or 0
    
    # 3. Processa dados para Gráfico e Lista
    minhas_notas = []
    chart_labels = []
    chart_data = []

    for h in historico:
        # Garante que nota seja float, mesmo se None no banco
        nota = float(h.media_final) if h.media_final is not None else 0.0
        
        # Tenta pegar nome da disciplina, com fallback
        try:
            disciplina_nome = h.turma_disciplina_professor.disciplina.nome
        except AttributeError:
            disciplina_nome = "Disciplina S/N"
        
        # Popula dados do gráfico
        chart_labels.append(disciplina_nome)
        chart_data.append(round(nota, 1))

        # Popula lista de notas
        cor = 'success'
        if nota < 6.0: cor = 'danger'
        elif nota < 7.0: cor = 'warning'
        
        # Tenta pegar o nome do professor
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

    # Dados JSON para o Chart.js
    dashboard_data = {
        'labels': chart_labels,
        'data': chart_data
    }

    # 4. Dados Financeiros
    pendencias_fin = Pagamento.objects.filter(aluno=request.user, status='pendente').exists()
    status_financeiro = "Pendente" if pendencias_fin else "Em Dia"
    cor_financeiro = "warning" if pendencias_fin else "success"

    context.update({
        'media_geral': round(media_geral, 1),
        'total_faltas': total_faltas,
        'minhas_notas': minhas_notas,
        'status_financeiro': status_financeiro,
        'cor_financeiro': cor_financeiro,
        # Passa o dict (não a string JSON) para que o template use `json_script` corretamente
        'dashboard_data_json': dashboard_data
    })
    return render(request, "dashboards/aluno_dashboard.html", context)

@rolerequired("secretaria", "coordenacao") 
def gestao_documentos_view(request):
    documentos = DocumentoEmitido.objects.select_related('aluno__user', 'solicitante').all()
    search_query = request.GET.get('q')
    if search_query:
        documentos = documentos.filter(
            Q(aluno__user__first_name__icontains=search_query) |
            Q(aluno__user__last_name__icontains=search_query) |
            Q(aluno__RA_aluno__icontains=search_query)
        )
    documentos = documentos[:50]
    alunos = Aluno.objects.select_related('user').all().order_by('user__first_name')
    context = {'documentos': documentos, 'alunos': alunos, 'search_query': search_query}
    return render(request, "dashboards/gestao_documentos.html", context)

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

# =============================================================================
# 4. APIs e PLACEHOLDERS
# =============================================================================

@rolerequired("secretaria")
def comunicacao_secretaria_view(request): return render(request, "dashboards/comunicacao_secretaria.html")
@rolerequired("aluno")
def boletim_view(request): return render(request, "dashboards/boletim.html")
@rolerequired("aluno")
def calendario_view(request): return render(request, "dashboards/calendario.html")
@rolerequired("aluno")
def avisos_eventos_view(request):
	from .models import Aviso, EventoAcademico
	from datetime import datetime
	agora = datetime.now()
	avisos = Aviso.objects.filter(ativo=True).exclude(data_fim_visibilidade__lt=agora).order_by('-data_publicacao')[:10]
	eventos = EventoAcademico.objects.filter(ativo=True, data_evento__gte=agora).order_by('data_evento')[:5]
	return render(request, "dashboards/avisos_eventos.html", {'avisos': avisos, 'eventos': eventos})

@login_required
def api_avisos_eventos(request):
	"""Retorna avisos e eventos para a home em JSON."""
	from .models import Aviso, EventoAcademico
	from datetime import datetime
	import json
	agora = datetime.now()
	avisos = Aviso.objects.filter(ativo=True).exclude(data_fim_visibilidade__lt=agora).order_by('-data_publicacao')[:5]
	eventos = EventoAcademico.objects.filter(ativo=True, data_evento__gte=agora).order_by('data_evento')[:3]
	
	avisos_data = [{
		'id': a.id,
		'titulo': a.titulo,
		'conteudo': a.conteudo,
		'tipo': a.tipo,
		'tipo_usuario': a.tipo_usuario_criador,
		'data': a.data_publicacao.strftime('%d/%m/%Y %H:%M'),
		'criador': a.criado_por.get_full_name() if a.criado_por else 'Sistema'
	} for a in avisos]
	
	eventos_data = [{
		'id': e.id,
		'titulo': e.titulo,
		'descricao': e.descricao,
		'data': e.data_evento.strftime('%d/%m/%Y'),
		'local': e.local
	} for e in eventos]
	
	return JsonResponse({'avisos': avisos_data, 'eventos': eventos_data})


@require_http_methods(["POST"])
@rolerequired('professor', 'coordenacao', 'secretaria')
def criar_aviso(request):
    """Cria um aviso via API. Espera JSON com: titulo, conteudo, tipo (Urgente/Importante/Geral/Informativo)."""
    from .models import Aviso
    import json
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

    titulo = payload.get('titulo')
    conteudo = payload.get('conteudo')
    tipo = payload.get('tipo') or 'Geral'

    if not titulo or not conteudo:
        return JsonResponse({'success': False, 'error': 'Título e conteúdo são obrigatórios.'}, status=400)

    # determinar tipo de usuário criador
    if isprofessor(request.user): tipo_usuario = 'professor'
    elif iscoordenacao(request.user): tipo_usuario = 'coordenacao'
    elif issecretaria(request.user): tipo_usuario = 'secretaria'
    else: tipo_usuario = 'secretaria'

    aviso = Aviso.objects.create(
        titulo=titulo,
        conteudo=conteudo,
        tipo=tipo,
        criado_por=request.user,
        tipo_usuario_criador=tipo_usuario
    )

    return JsonResponse({'success': True, 'aviso': {
        'id': aviso.id,
        'titulo': aviso.titulo,
        'conteudo': aviso.conteudo,
        'tipo': aviso.tipo,
        'tipo_usuario': aviso.tipo_usuario_criador,
        'data': aviso.data_publicacao.strftime('%d/%m/%Y %H:%M')
    }})


@require_http_methods(["POST"])
@rolerequired('professor', 'coordenacao', 'secretaria')
def criar_evento(request):
    """Cria um evento via API. Espera JSON com: titulo, descricao, data_evento (ISO yyyy-mm-dd or yyyy-mm-ddThh:mm), local."""
    from .models import EventoAcademico
    import json
    from datetime import datetime
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

    titulo = payload.get('titulo')
    descricao = payload.get('descricao', '')
    data_evento_raw = payload.get('data_evento')
    local = payload.get('local', '')

    if not titulo or not data_evento_raw:
        return JsonResponse({'success': False, 'error': 'Título e data do evento são obrigatórios.'}, status=400)

    # parse data_evento
    try:
        # try ISO first
        data_evento = datetime.fromisoformat(data_evento_raw)
    except Exception:
        try:
            data_evento = datetime.strptime(data_evento_raw, '%Y-%m-%d')
        except Exception:
            return JsonResponse({'success': False, 'error': 'Formato de data inválido.'}, status=400)

    if isprofessor(request.user): tipo_usuario = 'professor'
    elif iscoordenacao(request.user): tipo_usuario = 'coordenacao'
    elif issecretaria(request.user): tipo_usuario = 'secretaria'
    else: tipo_usuario = 'secretaria'

    evento = EventoAcademico.objects.create(
        titulo=titulo,
        descricao=descricao,
        data_evento=data_evento,
        criado_por=request.user,
        tipo_usuario_criador=tipo_usuario,
        local=local
    )

    return JsonResponse({'success': True, 'evento': {
        'id': evento.id,
        'titulo': evento.titulo,
        'descricao': evento.descricao,
        'data': evento.data_evento.strftime('%d/%m/%Y'),
        'local': evento.local
    }})

@login_required
def perfil_view(request): return render(request, "dashboards/perfil.html")

# APIs para Gestão de Alunos
@require_http_methods(["POST"])
@login_required 
def save_aluno_view(request): return JsonResponse({'success': True})
@require_http_methods(["DELETE", "POST"])
@login_required
def delete_aluno_view(request, pk): return JsonResponse({'success': True})

# Placeholders de Coordenação
@rolerequired("coordenacao")
def coordenacao_desempenho_view(request):
    """
    Gera um pacote mínimo de dados (turmas, alunos e gráficos) para a
    página de desempenho da coordenação. Os dados são serializados em JSON
    e injetados na template como `desempenho_data_json` (literal JSON seguro).
    """
    # Turmas - média e contagem de alunos
    turmas_qs = Turma.objects.all()
    turmas = []
    for t in turmas_qs:
        media_t = Historico.objects.filter(
            turma_disciplina_professor__turma=t
        ).aggregate(media=Avg('media_final'))['media'] or 0
        # tenta usar campo armazenado senão conta via relação
        alunos_count = t.alunos_matriculados if getattr(t, 'alunos_matriculados', None) else t.alunos.count() if hasattr(t, 'alunos') else 0
        turmas.append({
            'codigo': t.nome,
            'alunos': alunos_count,
            'nome': t.nome,
            'media_geral': round(media_t or 0, 1)
        })

    # Alunos - média e frequência agregadas por aluno (baseada em históricos)
    historicos = Historico.objects.select_related('id_aluno', 'id_aluno__user', 'turma_disciplina_professor__turma').all()
    alunos_map = {}
    for h in historicos:
        a = h.id_aluno
        key = a.user.id
        if key not in alunos_map:
            alunos_map[key] = {
                'nome': a.user.get_full_name(),
                'matricula': getattr(a, 'RA_aluno', ''),
                'turma': a.turma_atual.nome if getattr(a, 'turma_atual', None) else '',
                'media_sum': 0.0,
                'media_count': 0,
                'freq_sum': 0.0,
                'freq_count': 0
            }
        if h.media_final is not None:
            alunos_map[key]['media_sum'] += float(h.media_final)
            alunos_map[key]['media_count'] += 1
        if h.frequencia_percentual is not None:
            alunos_map[key]['freq_sum'] += float(h.frequencia_percentual)
            alunos_map[key]['freq_count'] += 1

    alunos = []
    aprovados = recuperacao = reprovados = 0
    for v in alunos_map.values():
        media = round((v['media_sum'] / v['media_count']) if v['media_count'] else 0, 1)
        freq = round((v['freq_sum'] / v['freq_count']) if v['freq_count'] else 0)
        if media >= 7.0:
            situacao = 'Aprovado'
            aprovados += 1
        elif media >= 5.0:
            situacao = 'Recuperação'
            recuperacao += 1
        else:
            situacao = 'Reprovado'
            reprovados += 1

        alunos.append({
            'nome': v['nome'],
            'matricula': v['matricula'],
            'turma': v['turma'],
            'media': media,
            'frequencia': freq,
            'situacao': situacao
        })

    grafico_notas = {
        'Aprovado': aprovados,
        'Recuperacao': recuperacao,
        'Reprovado': reprovados
    }

    grafico_frequencia = {
        'labels': [t['nome'] for t in turmas],
        'data': [
            round(Historico.objects.filter(turma_disciplina_professor__turma=Turma.objects.get(nome=t['nome'])).aggregate(freq=Avg('frequencia_percentual'))['freq'] or 0)
            for t in turmas
        ]
    }

    desempenho = {
        'turmas': turmas,
        'alunos': alunos,
        'grafico_notas': grafico_notas,
        'grafico_frequencia': grafico_frequencia
    }

    context = {
        'desempenho_data_json': json.dumps(desempenho, cls=DjangoJSONEncoder)
    }
    return render(request, "dashboards/coordenacao_desempenho.html", context)
@rolerequired("coordenacao")
def coordenacao_gestao_view(request):
    """
    Fornece dados em JSON para a página de Gestão da Coordenação.
    Gera objetos simples: alunos_json, turmas_json, professores_json, disciplinas_json
    que o template espera para renderização via JS.
    """
    # Alunos
    alunos_qs = Aluno.objects.select_related('user', 'turma_atual').all().order_by('user__first_name')
    alunos_json = []
    for a in alunos_qs:
        alunos_json.append({
            'nome': a.user.get_full_name(),
            'matricula': getattr(a, 'RA_aluno', ''),
            'turma': a.turma_atual.nome if getattr(a, 'turma_atual', None) else '',
            'status': getattr(a, 'status_matricula', '')
        })

    # Turmas
    turmas_qs = Turma.objects.select_related('id_curso').all().order_by('nome')
    turmas_json = []
    for t in turmas_qs:
        vagas = getattr(t, 'capacidade_maxima', 0)
        matriculados = getattr(t, 'alunos_matriculados', None)
        if matriculados is None:
            # tenta contar relação 'alunos' se existir
            matriculados = t.alunos.count() if hasattr(t, 'alunos') else 0
        turmas_json.append({
            'codigo': t.nome,
            'nome': t.id_curso.nome_curso if getattr(t, 'id_curso', None) else t.nome,
            'professor': '',
            'matriculados': matriculados,
            'vagas': vagas
        })

    # Professores
    prof_qs = Professor.objects.select_related('user').all().order_by('user__first_name')
    professores_json = []
    for p in prof_qs:
        # disciplinas e turmas associados podem ser obtidos via TurmaDisciplinaProfessor
        tdp = TurmaDisciplinaProfessor.objects.filter(professor=p).select_related('disciplina')
        disciplinas = ','.join(sorted(set([d.disciplina.nome for d in tdp if d.disciplina])))
        turmas_count = tdp.values('turma').distinct().count()
        professores_json.append({
            'nome': p.user.get_full_name(),
            'email': p.user.email,
            'disciplinas': disciplinas or '',
            'turmas': turmas_count
        })

    # Disciplinas
    disc_qs = Disciplina.objects.all().order_by('cod_disciplina')
    disciplinas_json = []
    for d in disc_qs:
        # número de turmas onde a disciplina está alocada
        uso = TurmaDisciplinaProfessor.objects.filter(disciplina=d).values('turma').distinct().count()
        disciplinas_json.append({
            'codigo': d.cod_disciplina,
            'nome': d.nome,
            'cargaHoraria': d.carga_horaria or 0,
            'turmas': uso
        })

    context = {
        'alunos_json': json.dumps(alunos_json, cls=DjangoJSONEncoder),
        'turmas_json': json.dumps(turmas_json, cls=DjangoJSONEncoder),
        'professores_json': json.dumps(professores_json, cls=DjangoJSONEncoder),
        'disciplinas_json': json.dumps(disciplinas_json, cls=DjangoJSONEncoder)
    }
    return render(request, "dashboards/coordenacao_gestao.html", context)
@login_required
def coordenacao_comunicacao_view(request): return render(request, "dashboards/coordenacao_comunicacao.html")
@login_required
def coordenacao_relatorios_view(request): return render(request, "dashboards/coordenacao_relatorios.html")

# Avisos e Eventos - Criação
@login_required
def criar_aviso(request):
	"""Permite que professor, coordenador ou secretária crie um aviso."""
	from .models import Aviso
	user_type = getattr(request.user.profile, 'tipo', None) if hasattr(request.user, 'profile') else None
	if user_type not in ['professor', 'coordenacao', 'secretaria']:
		return JsonResponse({'error': 'Sem permissão'}, status=403)
	
	if request.method == 'POST':
		titulo = request.POST.get('titulo', '')
		conteudo = request.POST.get('conteudo', '')
		tipo = request.POST.get('tipo', 'Geral')
		aviso = Aviso.objects.create(
			titulo=titulo,
			conteudo=conteudo,
			tipo=tipo,
			criado_por=request.user,
			tipo_usuario_criador=user_type
		)
		return JsonResponse({'id': aviso.id, 'success': True})
	return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def criar_evento(request):
	"""Permite que professor, coordenador ou secretária crie um evento."""
	from .models import EventoAcademico
	user_type = getattr(request.user.profile, 'tipo', None) if hasattr(request.user, 'profile') else None
	if user_type not in ['professor', 'coordenacao', 'secretaria']:
		return JsonResponse({'error': 'Sem permissão'}, status=403)
	
	if request.method == 'POST':
		titulo = request.POST.get('titulo', '')
		descricao = request.POST.get('descricao', '')
		data_evento = request.POST.get('data_evento', '')
		local = request.POST.get('local', '')
		try:
			from datetime import datetime
			data = datetime.fromisoformat(data_evento.replace('Z', '+00:00'))
			evento = EventoAcademico.objects.create(
				titulo=titulo,
				descricao=descricao,
				data_evento=data,
				local=local,
				criado_por=request.user,
				tipo_usuario_criador=user_type
			)
			return JsonResponse({'id': evento.id, 'success': True})
		except Exception as e:
			return JsonResponse({'error': str(e)}, status=400)
	return JsonResponse({'error': 'Method not allowed'}, status=405)

# APIs JSON de Coordenação
@login_required
def api_coordenacao_kpis(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_desempenho(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_aprovacao(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_atividades(request): return JsonResponse({'status': 'ok'})