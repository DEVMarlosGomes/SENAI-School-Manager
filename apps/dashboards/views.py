import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Avg, Count, Q, Sum
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from django.urls import reverse
import os

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
    """
    Decorator personalizado para verificar permissões de acesso baseadas no perfil.
    """
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
# 2. VIEW PRINCIPAL (HOME)
# =============================================================================

def home(request):
    """
    Página inicial pública.
    Se o usuário estiver logado, redireciona para o dashboard.
    Se não, mostra a landing page com estatísticas.
    """
    if request.user.is_authenticated:
        if isaluno(request.user): return redirect('aluno_dashboard')
        elif isprofessor(request.user): return redirect('professor_dashboard')
        elif issecretaria(request.user): return redirect('secretaria_dashboard')
        elif iscoordenacao(request.user): return redirect('coordenacao_dashboard')
    
    # Lógica adicionada para recuperar os dados do Dashboard Institucional
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_cursos = Curso.objects.count()

    # Cálculo da taxa de aprovação (Baseado em históricos com média >= 6.0)
    historicos_validos = Historico.objects.exclude(media_final__isnull=True)
    total_notas = historicos_validos.count()
    aprovacoes = historicos_validos.filter(media_final__gte=6.0).count()
    
    taxa_aprovacao = (aprovacoes / total_notas * 100) if total_notas > 0 else 0
    
    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_cursos': total_cursos,
        'taxa_aprovacao': taxa_aprovacao
    }
    
    return render(request, "home.html", context)

# =============================================================================
# 3. SISTEMA DE APROVAÇÕES
# =============================================================================

@rolerequired("coordenacao")
def coordenacao_aprovacao_view(request):
    """
    Gestão de Aprovações Pendentes (Usuários e Turmas).
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        motivo = request.POST.get('motivo_rejeicao', '')

        try:
            if action in ['approve_user', 'reject_user']:
                registro = PendingRegistration.objects.get(id=item_id)
                
                if action == 'approve_user':
                    if registro.status == 'aprovado':
                         messages.warning(request, f"O usuário {registro.username} já foi aprovado.")
                    else:
                        novo_user = registro.aprovar(admin_user=request.user)
                        messages.success(request, f"Cadastro de {novo_user.get_full_name()} aprovado com sucesso!")
                
                elif action == 'reject_user':
                    registro.rejeitar(admin_user=request.user, motivo=motivo)
                    messages.warning(request, f"Cadastro rejeitado.")

            elif action in ['approve_turma', 'reject_turma']:
                turma = Turma.objects.get(id=item_id)
                
                if action == 'approve_turma':
                    turma.status_aprovacao = 'Aprovada'
                    if hasattr(request.user, 'coordenacao'):
                        turma.coordenacao_aprovacao = request.user.coordenacao
                    turma.save()
                    messages.success(request, f"Turma {turma.nome} aprovada.")
                
                elif action == 'reject_turma':
                    turma.status_aprovacao = 'Rejeitada'
                    turma.save() 
                    messages.warning(request, f"Turma {turma.nome} rejeitada.")

        except Exception as e:
            messages.error(request, f"Erro ao processar: {str(e)}")
        
        return redirect('coordenacao_aprovacao')

    registros_pendentes = PendingRegistration.objects.filter(status='pendente').order_by('data_solicitacao')
    turmas_pendentes = Turma.objects.filter(status_aprovacao='Pendente').select_related('id_curso').order_by('data_inicio')

    context = {
        'registros_pendentes': registros_pendentes,
        'turmas_pendentes': turmas_pendentes,
    }
    return render(request, "dashboards/coordenacao_aprovacao.html", context)

# =============================================================================
# 4. DASHBOARDS E GESTÃO
# =============================================================================

@rolerequired("secretaria", "coordenacao")
def gestao_alunos_view(request):
    alunos_qs = Aluno.objects.select_related(
        'user', 'user__profile', 'turma_atual', 'turma_atual__id_curso'
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
    
    pode_editar = (getattr(request.user.profile, 'tipo', '') == 'coordenacao')

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
    for hist in historicos_alunos:
        motivo = []
        nota = float(hist.media_final) if hist.media_final is not None else 0.0
        freq = float(hist.frequencia_percentual) if hist.frequencia_percentual is not None else 0.0

        if nota < 6.0: motivo.append(f"Nota: {nota}")
        if freq < 75.0: motivo.append(f"Freq: {freq:.0f}%")
        
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
    
    total_alunos = Aluno.objects.count()
    total_turmas = Turma.objects.count()
    matriculas_ativas = Aluno.objects.filter(status_matricula='Ativo').count()
    pgtos_pendentes_count = Pagamento.objects.filter(status='pendente').count()
    
    docs_recentes = DocumentoEmitido.objects.select_related(
        'aluno', 'aluno__user'
    ).order_by('-data_emissao')[:5]

    context.update({
        'total_alunos': total_alunos,
        'total_turmas': total_turmas,
        'matriculas_ativas': matriculas_ativas,
        'pgtos_pendentes': pgtos_pendentes_count,
        'docs_recentes': docs_recentes,
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
            if m >= 7.0: apro += 1
            elif m >= 5.0: rec += 1
            else: rep += 1

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

    dashboard_data = {
        'labels': chart_labels,
        'data': chart_data
    }

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

@rolerequired("secretaria")
def comunicacao_secretaria_view(request): return render(request, "dashboards/comunicacao_secretaria.html")

@rolerequired("aluno")
def boletim_view(request):
    try:
        aluno = Aluno.objects.select_related('user', 'turma_atual', 'turma_atual__id_curso').get(user=request.user)
    except Aluno.DoesNotExist:
        messages.error(request, "Perfil de aluno não encontrado.")
        return redirect('home')

    historicos = Historico.objects.filter(id_aluno=aluno).select_related(
        'turma_disciplina_professor__disciplina',
        'turma_disciplina_professor__professor__user',
        'turma_disciplina_professor__turma'
    ).order_by('-periodo_realizacao', 'turma_disciplina_professor__disciplina__nome')

    boletim_por_periodo = {}
    total_disciplinas = 0
    soma_medias = 0
    
    for h in historicos:
        periodo = h.periodo_realizacao
        if periodo not in boletim_por_periodo:
            boletim_por_periodo[periodo] = []
        
        cor_status = 'success'
        if h.media_final is not None:
            if h.media_final < 5.0: cor_status = 'danger'
            elif h.media_final < 7.0: cor_status = 'warning'
            soma_medias += h.media_final
            total_disciplinas += 1

        h.cor_status = cor_status
        h.professor_nome = h.turma_disciplina_professor.professor.user.get_full_name() if h.turma_disciplina_professor.professor else "Não atribuído"
        h.disciplina_nome = h.turma_disciplina_professor.disciplina.nome
        boletim_por_periodo[periodo].append(h)

    cr_geral = round(soma_medias / total_disciplinas, 2) if total_disciplinas > 0 else 0

    context = {
        'aluno': aluno,
        'boletim_por_periodo': boletim_por_periodo,
        'cr_geral': cr_geral,
        'total_disciplinas': total_disciplinas
    }
    return render(request, "dashboards/boletim.html", context)

@rolerequired("aluno")
def calendario_view(request): return render(request, "dashboards/calendario.html")

@rolerequired("aluno")
def avisos_eventos_view(request):
    # AVISOS e EVENTOS - Placeholder ou buscar de models se existirem
    return render(request, "dashboards/avisos_eventos.html", {})

@login_required
def api_avisos_eventos(request):
    return JsonResponse({'avisos': [], 'eventos': []})

@require_http_methods(["POST"])
@rolerequired('professor', 'coordenacao', 'secretaria')
def criar_aviso(request):
    return JsonResponse({'success': True})

@require_http_methods(["POST"])
@rolerequired('professor', 'coordenacao', 'secretaria')
def criar_evento(request):
    return JsonResponse({'success': True})

# =============================================================================
# 5. PERFIL (CORRIGIDO)
# =============================================================================

@login_required
def perfil_view(request):
    """
    Exibe o perfil do usuário carregando os dados específicos (Aluno, Professor, etc)
    para preencher os campos do template corretamente.
    """
    context = {}
    
    try:
        # Verifica se o usuário tem perfil
        if not hasattr(request.user, 'profile'):
            context['tipo_usuario'] = 'desconhecido'
            return render(request, "dashboards/perfil.html", context)
            
        profile = request.user.profile
        context['tipo_usuario'] = profile.tipo
        
        # === Lógica para ALUNO ===
        if profile.tipo == 'aluno':
            try:
                # Busca o aluno trazendo junto a turma e o curso e o endereço
                aluno = Aluno.objects.select_related('turma_atual', 'turma_atual__id_curso', 'cod_endereco').get(user=request.user)
                context['perfil_dado'] = aluno
                
                # Se o aluno tiver turma, adiciona turma e curso ao contexto
                if aluno.turma_atual:
                    context['turma'] = aluno.turma_atual
                    context['curso'] = aluno.turma_atual.id_curso
            except Aluno.DoesNotExist:
                context['erro_perfil'] = "Registro de aluno não encontrado."

        # === Lógica para PROFESSOR ===
        elif profile.tipo == 'professor':
            try:
                professor = Professor.objects.select_related('cod_endereco').get(user=request.user)
                context['perfil_dado'] = professor
                
                # Conta turmas onde o professor está alocado
                qtd_turmas = TurmaDisciplinaProfessor.objects.filter(professor=professor).values('turma').distinct().count()
                context['qtd_turmas'] = qtd_turmas
            except Professor.DoesNotExist:
                context['erro_perfil'] = "Registro de professor não encontrado."

        # === Lógica para SECRETARIA ===
        elif profile.tipo == 'secretaria':
            try:
                context['perfil_dado'] = Secretaria.objects.select_related('cod_endereco').get(user=request.user)
            except Secretaria.DoesNotExist:
                pass

        # === Lógica para COORDENAÇÃO ===
        elif profile.tipo == 'coordenacao':
            try:
                context['perfil_dado'] = Coordenacao.objects.select_related('cod_endereco').get(user=request.user)
            except Coordenacao.DoesNotExist:
                pass

    except Exception as e:
        context['erro_perfil'] = f"Erro inesperado ao carregar perfil: {str(e)}"
        
    return render(request, "dashboards/perfil.html", context)

# =============================================================================
# 6. FUNÇÕES ESPECÍFICAS DE COORDENAÇÃO (CORRIGIDAS)
# =============================================================================

@rolerequired("coordenacao")
def coordenacao_desempenho_view(request):
    # --- 1. Dados das Turmas e Gráfico de Frequência ---
    turmas_qs = Turma.objects.all()
    turmas_data = []
    
    # Listas para o gráfico de frequência (Barras)
    freq_labels = []
    freq_values = []

    for t in turmas_qs:
        # Calcula média e frequência agregada da turma
        stats = Historico.objects.filter(turma_disciplina_professor__turma=t).aggregate(
            media_t=Avg('media_final'),
            freq_t=Avg('frequencia_percentual')
        )
        
        media_t = stats['media_t'] or 0
        freq_t = stats['freq_t'] or 0
        alunos_count = t.alunos_matriculados 

        turmas_data.append({
            'codigo': t.nome,
            'alunos': alunos_count,
            'nome': t.nome, 
            'media_geral': round(media_t, 1)
        })

        freq_labels.append(t.nome)
        freq_values.append(round(freq_t, 1))

    # --- 2. Dados dos Alunos e Gráfico de Notas ---
    alunos_qs = Aluno.objects.select_related('user', 'turma_atual').all()
    alunos_data = []
    
    status_counts = {
        'Aprovado': 0, 
        'Recuperação': 0, 
        'Reprovado': 0
    }

    for aluno in alunos_qs:
        hists = Historico.objects.filter(id_aluno=aluno)
        
        if not hists.exists():
            media_a = 0.0
            freq_a = 0.0
            situacao = 'Cursando' 
        else:
            agg = hists.aggregate(
                media_a=Avg('media_final'),
                freq_a=Avg('frequencia_percentual')
            )
            media_a = float(agg['media_a'] or 0.0)
            freq_a = float(agg['freq_a'] or 0.0)
            
            if media_a >= 7.0 and freq_a >= 75.0:
                situacao = 'Aprovado'
                status_counts['Aprovado'] += 1
            elif media_a < 5.0 or freq_a < 75.0:
                situacao = 'Reprovado'
                status_counts['Reprovado'] += 1
            else:
                situacao = 'Recuperação'
                status_counts['Recuperação'] += 1

        alunos_data.append({
            'nome': aluno.user.get_full_name(),
            'matricula': aluno.RA_aluno,
            'turma': aluno.turma_atual.nome if aluno.turma_atual else 'Sem Turma',
            'media': round(media_a, 1),
            'frequencia': round(freq_a, 1),
            'situacao': situacao
        })

    desempenho = {
        'turmas': turmas_data,
        'alunos': alunos_data,
        'grafico_notas': status_counts, 
        'grafico_frequencia': {
            'labels': freq_labels,
            'data': freq_values
        }
    }
    
    context = {'desempenho_data_json': json.dumps(desempenho, cls=DjangoJSONEncoder)}
    return render(request, "dashboards/coordenacao_desempenho.html", context)

@rolerequired("coordenacao")
def coordenacao_gestao_view(request):
    """
    Dashboard de Gestão Acadêmica.
    Agora prepara dados completos para manipulação via Modal/API.
    """
    
    # 1. ALUNOS
    alunos_qs = Aluno.objects.select_related('user', 'turma_atual').all().order_by('user__first_name')
    alunos_json = []
    for a in alunos_qs:
        alunos_json.append({
            'id': a.pk,
            'nome': a.user.get_full_name(),
            'email': a.user.email,
            'matricula': a.RA_aluno,
            'turma_id': a.turma_atual.pk if a.turma_atual else '',
            'turma_nome': a.turma_atual.nome if a.turma_atual else 'Sem Turma',
            'status': a.status_matricula
        })

    # 2. TURMAS
    turmas_qs = Turma.objects.select_related('id_curso').all().order_by('nome')
    turmas_json = []
    for t in turmas_qs:
        turmas_json.append({
            'id': t.pk,
            'codigo': t.nome,
            'curso_id': t.id_curso.pk,
            'curso_nome': t.id_curso.nome_curso,
            'matriculados': t.alunos_matriculados,
            'vagas': t.capacidade_maxima,
            'data_inicio': t.data_inicio.strftime('%Y-%m-%d') if t.data_inicio else '',
            'data_fim': t.data_fim.strftime('%Y-%m-%d') if t.data_fim else ''
        })
    
    # 3. PROFESSORES
    professores_qs = Professor.objects.select_related('user').all()
    professores_json = []
    for p in professores_qs:
        qtd_turmas = TurmaDisciplinaProfessor.objects.filter(professor=p).values('turma').distinct().count()
        professores_json.append({
            'id': p.pk,
            'nome': p.user.get_full_name(),
            'email': p.user.email,
            'registro': p.registro_funcional or '',
            'turmas': qtd_turmas
        })

    # 4. DISCIPLINAS
    disciplinas_qs = Disciplina.objects.all().order_by('nome')
    disciplinas_json = []
    for d in disciplinas_qs:
        disciplinas_json.append({
            'id': d.pk,
            'codigo': d.cod_disciplina,
            'nome': d.nome,
            'carga_horaria': d.carga_horaria
        })

    # Listas Auxiliares
    cursos_list = list(Curso.objects.values('id', 'nome_curso'))

    context = {
        'alunos_json': json.dumps(alunos_json, cls=DjangoJSONEncoder),
        'turmas_json': json.dumps(turmas_json, cls=DjangoJSONEncoder),
        'professores_json': json.dumps(professores_json, cls=DjangoJSONEncoder),
        'disciplinas_json': json.dumps(disciplinas_json, cls=DjangoJSONEncoder),
        'cursos_json': json.dumps(cursos_list, cls=DjangoJSONEncoder)
    }
    
    return render(request, "dashboards/coordenacao_gestao.html", context)

# =============================================================================
# 7. APIS PARA GESTÃO (CRUD)
# =============================================================================

# --- ALUNO ---
@require_http_methods(["POST"])
@login_required
def save_aluno_view(request):
    try:
        data = json.loads(request.body)
        aluno_id = data.get('id')
        
        with transaction.atomic():
            if aluno_id:
                # Edição
                aluno = Aluno.objects.get(pk=aluno_id)
                user = aluno.user
                
                parts = data.get('nome', '').split(' ')
                user.first_name = parts[0]
                user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                
                user.email = data.get('email')
                user.save()
                
                aluno.RA_aluno = data.get('matricula')
                aluno.status_matricula = data.get('status')
                
                turma_id = data.get('turma')
                if turma_id:
                    aluno.turma_atual = Turma.objects.get(pk=turma_id)
                else:
                    aluno.turma_atual = None
                aluno.save()
                msg = "Aluno atualizado com sucesso."
            else:
                # Criação
                username = data.get('matricula')
                if User.objects.filter(username=username).exists():
                     return JsonResponse({'success': False, 'message': 'Usuário/Matrícula já existe.'})

                parts = data.get('nome', '').split(' ')
                first = parts[0]
                last = ' '.join(parts[1:]) if len(parts) > 1 else ''

                user = User.objects.create_user(
                    username=username,
                    email=data.get('email'),
                    password='mudar123',
                    first_name=first,
                    last_name=last
                )
                
                Profile.objects.create(user=user, tipo='aluno')

                turma_id = data.get('turma')
                turma_obj = Turma.objects.get(pk=turma_id) if turma_id else None
                
                Aluno.objects.create(
                    user=user,
                    RA_aluno=data.get('matricula'),
                    status_matricula=data.get('status', 'Ativo'),
                    turma_atual=turma_obj
                )
                msg = "Aluno criado com sucesso."

        return JsonResponse({'success': True, 'message': msg})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_http_methods(["DELETE"])
@login_required
def delete_aluno_view(request, pk):
    try:
        aluno = Aluno.objects.get(pk=pk)
        aluno.user.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# --- TURMA ---
@require_http_methods(["POST"])
@login_required
def save_turma_view(request):
    try:
        data = json.loads(request.body)
        turma_id = data.get('id')
        
        curso = Curso.objects.get(pk=data.get('curso'))
        
        defaults = {
            'nome': data.get('codigo'),
            'id_curso': curso,
            'capacidade_maxima': int(data.get('vagas', 40)),
            'periodo': 'Noturno',
            'ano_letivo': 2025,
            'data_inicio': data.get('data_inicio'),
            'data_fim': data.get('data_fim') if data.get('data_fim') else None
        }

        if turma_id:
            Turma.objects.filter(pk=turma_id).update(**defaults)
            msg = "Turma atualizada."
        else:
            Turma.objects.create(**defaults)
            msg = "Turma criada."
            
        return JsonResponse({'success': True, 'message': msg})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_http_methods(["DELETE"])
@login_required
def delete_turma_view(request, pk):
    try:
        Turma.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# --- PROFESSOR ---
@require_http_methods(["POST"])
@login_required
def save_professor_view(request):
    try:
        data = json.loads(request.body)
        prof_id = data.get('id')
        
        with transaction.atomic():
            if prof_id:
                prof = Professor.objects.get(pk=prof_id)
                user = prof.user
                
                parts = data.get('nome', '').split(' ')
                user.first_name = parts[0]
                user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                
                user.email = data.get('email')
                user.save()
                
                prof.registro_funcional = data.get('registro')
                prof.save()
                msg = "Professor atualizado."
            else:
                username = data.get('email').split('@')[0]
                if User.objects.filter(username=username).exists():
                     return JsonResponse({'success': False, 'message': 'Usuário já existe.'})

                parts = data.get('nome', '').split(' ')
                first = parts[0]
                last = ' '.join(parts[1:]) if len(parts) > 1 else ''

                user = User.objects.create_user(
                    username=username,
                    email=data.get('email'),
                    password='mudar123',
                    first_name=first,
                    last_name=last
                )
                Profile.objects.create(user=user, tipo='professor')
                
                Professor.objects.create(user=user, registro_funcional=data.get('registro'))
                msg = "Professor criado."

        return JsonResponse({'success': True, 'message': msg})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_http_methods(["DELETE"])
@login_required
def delete_professor_view(request, pk):
    try:
        prof = Professor.objects.get(pk=pk)
        prof.user.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# --- DISCIPLINA ---
@require_http_methods(["POST"])
@login_required
def save_disciplina_view(request):
    try:
        data = json.loads(request.body)
        disc_id = data.get('id')
        
        defaults = {
            'nome': data.get('nome'),
            'cod_disciplina': data.get('codigo'),
            'carga_horaria': int(data.get('carga_horaria', 0))
        }

        if disc_id:
            Disciplina.objects.filter(pk=disc_id).update(**defaults)
            msg = "Disciplina atualizada."
        else:
            Disciplina.objects.create(**defaults)
            msg = "Disciplina criada."
            
        return JsonResponse({'success': True, 'message': msg})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_http_methods(["DELETE"])
@login_required
def delete_disciplina_view(request, pk):
    try:
        Disciplina.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# =============================================================================
# 8. OUTRAS VIEWS E PLACEHOLDERS
# =============================================================================

@login_required
def coordenacao_comunicacao_view(request): return render(request, "dashboards/coordenacao_comunicacao.html")
@login_required
def coordenacao_relatorios_view(request): return render(request, "dashboards/coordenacao_relatorios.html")

@login_required
def api_coordenacao_kpis(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_desempenho(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_aprovacao(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_atividades(request): return JsonResponse({'status': 'ok'})