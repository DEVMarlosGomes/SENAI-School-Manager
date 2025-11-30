import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
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
# 3. DASHBOARDS E GESTÃO DE ALUNOS (Corrigido)
# =============================================================================

# ... (MANTENHA OS IMPORTS) ...

@rolerequired("secretaria", "coordenacao")
def gestao_alunos_view(request):
    """
    Lista de alunos com busca, filtros avançados e paginação.
    """
    # 1. Base Queryset (Otimizada)
    alunos_qs = Aluno.objects.select_related(
        'user', 
        'user__profile',
        'turma_atual',
        'turma_atual__id_curso'
    ).all().order_by('user__first_name')
    
    # 2. Filtros
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

    # 3. Dados para os Dropdowns de Filtro
    turmas_disponiveis = Turma.objects.all().order_by('nome')
    status_choices = ['Ativo', 'Inativo', 'Trancado', 'Formado'] # Ou pegue do model se preferir

    # 4. Paginação
    paginator = Paginator(alunos_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 5. Permissão de Edição (Só Coordenador)
    # Verifica se o perfil é estritamente 'coordenacao'
    pode_editar = (request.user.profile.tipo == 'coordenacao')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_turma': filter_turma, # Para manter selecionado no HTML
        'filter_status': filter_status,
        'total_alunos': total_alunos,
        'turmas': turmas_disponiveis,
        'status_choices': status_choices,
        'pode_editar': pode_editar # Variável chave para o template
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

    # Gráfico simples
    grafico_qs = Historico.objects.filter(turma_disciplina_professor__professor=professor)\
        .values('turma_disciplina_professor__turma__nome').annotate(media=Avg('media_final'))
    
    chart_labels = [i['turma_disciplina_professor__turma__nome'] for i in grafico_qs]
    chart_data = [round(i['media'] or 0, 1) for i in grafico_qs]
    if not chart_labels: chart_labels, chart_data = ["Sem dados"], [0]

    dashboard_data = {'labels': chart_labels, 'data': chart_data}

    context.update({
        'total_turmas': total_turmas,
        'total_alunos': total_alunos,
        'pendencias': pendencias,
        'dashboard_data_json': json.dumps(dashboard_data, cls=DjangoJSONEncoder),
        'turma_destaque': alocacoes.first().turma if alocacoes.exists() else None,
        'alunos_risco': [] 
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
    
    context.update({
        'total_alunos': Aluno.objects.count(),
        'total_professores': Professor.objects.count(),
        'total_turmas': Turma.objects.count(),
        'alunos_risco': 0,
        'dashboard_data_json': json.dumps({'scatter_data': {'bom': [], 'atencao': [], 'risco': []}})
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
    context = {
        'pagamentos': pagamentos,
        'kpi_recebido': recebido,
        'kpi_pendente': pendente,
        'kpi_inadimplencia': 0,
        'alunos_para_select': Aluno.objects.select_related('user').all()
    }
    return render(request, "dashboards/controle_financeiro.html", context)

@rolerequired("aluno")
def aluno_financeiro_view(request):
    pagamentos = Pagamento.objects.filter(aluno=request.user).order_by('-data_criacao')
    total = sum(p.valor for p in pagamentos.filter(status='pendente'))
    context = {'pagamentos': pagamentos, 'total_pendente': total}
    return render(request, "dashboards/aluno_financeiro.html", context)

# Placeholders e APIs auxiliares
@rolerequired("secretaria")
def gestao_documentos_view_old(request): return render(request, "dashboards/gestao_documentos.html")
@rolerequired("secretaria")
def gestao_documentos_view_placeholder(request): return render(request, "dashboards/gestao_documentos.html")
@rolerequired("secretaria")
def comunicacao_secretaria_view(request): return render(request, "dashboards/comunicacao_secretaria.html")
@rolerequired("aluno")
def materiais_estudo_view(request): return render(request, "dashboards/materiais_estudo.html")
@rolerequired("aluno")
def boletim_view(request): return render(request, "dashboards/boletim.html")
@rolerequired("aluno")
def calendario_view(request): return render(request, "dashboards/calendario.html")
@rolerequired("aluno")
def avisos_eventos_view(request): return render(request, "dashboards/avisos_eventos.html")
@login_required
def perfil_view(request): return render(request, "dashboards/perfil.html")
@require_http_methods(["POST"])
@login_required 
def save_aluno_view(request): return JsonResponse({'success': True})
@require_http_methods(["DELETE", "POST"])
@login_required
def delete_aluno_view(request, pk): return JsonResponse({'success': True})
@login_required
def coordenacao_desempenho_view(request): return render(request, "dashboards/coordenacao_desempenho.html")
@login_required
def coordenacao_gestao_view(request): return render(request, "dashboards/coordenacao_gestao.html")
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