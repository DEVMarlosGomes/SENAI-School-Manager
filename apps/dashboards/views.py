from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from datetime import date
import json
import csv

# Importa os NOVOS modelos funcionais
from apps.academico.models import (
    Turma, Aluno, Professor, Secretaria, Coordenacao, 
    Historico, Curso, TurmaDisciplinaProfessor
)
from .models import Material # O seu modelo de Material (assumindo que está em apps/dashboards/models.py)

# #####################################################################
# 🔒 NOVAS Funções de Verificação de Permissão
# (Substituem a lógica do 'Profile' antigo)
# #####################################################################

def is_aluno(user):
    return user.is_authenticated and Aluno.objects.filter(user=user).exists()

def is_professor(user):
    return user.is_authenticated and Professor.objects.filter(user=user).exists()

def is_secretaria(user):
    return user.is_authenticated and Secretaria.objects.filter(user=user).exists()

def is_coordenacao(user):
    return user.is_authenticated and Coordenacao.objects.filter(user=user).exists()

def role_required(*roles):
    """Decorator atualizado para verificar os novos modelos 1-para-1."""
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            user_roles = []
            if is_aluno(request.user): user_roles.append('aluno')
            if is_professor(request.user): user_roles.append('professor')
            if is_secretaria(request.user): user_roles.append('secretaria')
            if is_coordenacao(request.user): user_roles.append('coordenacao')

            # Verifica se o usuário tem *pelo menos um* dos papéis necessários
            if not any(role in roles for role in user_roles):
                messages.error(request, "Acesso negado a esta área.")
                return redirect('redirecionar_dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------
# 🌐 Home (Atualizada)
# ---------------------------------------------------------------------
@login_required
def home(request):
    # Redireciona com base nos novos modelos
    if is_aluno(request.user):
        return redirect('aluno_dashboard')
    elif is_professor(request.user):
        return redirect('professor_dashboard')
    elif is_secretaria(request.user):
        return redirect('secretaria_dashboard')
    elif is_coordenacao(request.user):
        return redirect('coordenacao_dashboard')
    elif request.user.is_staff: # Para o admin/superusuário
        return redirect('secretaria_dashboard') # ou 'coordenacao_dashboard'
    
    # Se não tiver papel, vai para a home (ou uma pág de "perfil incompleto")
    return render(request, 'home.html')

# ---------------------------------------------------------------------
# 🎓 Dashboard do Aluno (Atualizado)
# ---------------------------------------------------------------------
@role_required('aluno')
def aluno_dashboard_view(request):
    aluno = Aluno.objects.get(user=request.user)
    
    # Lógica de notas e faltas agora vem do 'Historico'
    notas_recentes = Historico.objects.filter(id_aluno=aluno).exclude(nota_final=None).order_by('-data_lancamento')[:5]
    faltas_recentes = Historico.objects.filter(id_aluno=aluno).exclude(total_faltas=None).order_by('-data_lancamento')[:5]

    context = {
        'titulo': 'Dashboard do Aluno',
        'notas_recentes': notas_recentes,
        'faltas_recentes': faltas_recentes,
        # ... (avisos e eventos estáticos mantidos) ...
        'avisos': [
            {'titulo': 'Alteração no Cronograma', 'tipo': 'Urgente', 'mensagem': 'As aulas de programação foram remanejadas para terça-feira.', 'data': '2025-11-10'},
        ],
        'eventos': [
            {'titulo': 'Workshop de Inovação', 'data': date(2025, 11, 25), 'hora_inicio': '14:00', 'hora_fim': '17:00', 'local': 'Auditório Principal'},
        ],
    }
    return render(request, 'dashboards/aluno_dashboard.html', context)


# ---------------------------------------------------------------------
# 📚 Materiais de Estudo (Mantido como estava, mas com decorator atualizado)
# ---------------------------------------------------------------------
@role_required('aluno', 'professor', 'coordenacao')
def materiais_estudo_view(request):
    q = (request.GET.get('q') or '').strip().lower()
    disciplina_filter = (request.GET.get('disciplina') or '').strip()
    tipo_filter = (request.GET.get('tipo') or '').strip()
    order = (request.GET.get('order') or 'data_desc')
    page = request.GET.get('page', 1)

    qs = Material.objects.all()
    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(descricao__icontains=q) | Q(disciplina__icontains=q))
    if disciplina_filter:
        qs = qs.filter(disciplina=disciplina_filter)
    if tipo_filter:
        qs = qs.filter(tipo=tipo_filter)

    qs = qs.order_by('-criado_em' if order == 'data_desc' else 'criado_em')

    paginator = Paginator(qs, 6)
    try:
        materiais_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        materiais_page = paginator.page(1)

    disciplinas = sorted(list(Material.objects.values_list('disciplina', flat=True).distinct()))
    tipos = sorted(list(Material.objects.values_list('tipo', flat=True).distinct()))

    context = {
        'titulo': 'Materiais de Estudo',
        'materiais': materiais_page,
        'disciplinas': disciplinas,
        'tipos': tipos,
        'q': q,
        'disciplina_selected': disciplina_filter,
        'tipo_selected': tipo_filter,
        'order_selected': order,
        'paginator': paginator,
    }
    return render(request, 'dashboards/materiais_estudo.html', context)


# ---------------------------------------------------------------------
# 🗓️ Calendário (Aluno) (Mantido)
# ---------------------------------------------------------------------
@role_required('aluno')
def calendario_view(request):
    eventos = [
        {'title': 'Semana de Provas', 'start': '2025-11-11', 'end': '2025-11-15', 'color': '#0d6efd'},
        {'title': 'Entrega de Trabalhos', 'start': '2025-11-20', 'color': '#198754'},
        {'title': 'Feira de Ciências', 'start': '2025-12-05', 'color': '#ffc107'},
    ]
    return render(request, 'dashboards/calendario.html', {'eventos': json.dumps(eventos)})


# ---------------------------------------------------------------------
# 👩‍🏫 Dashboard do Professor (Atualizado)
# ---------------------------------------------------------------------
@role_required('professor')
def professor_dashboard_view(request):
    professor = Professor.objects.get(user=request.user)
    
    # Acessa as alocações do professor
    alocacoes = TurmaDisciplinaProfessor.objects.filter(professor=professor)
    
    # Pega os IDs das turmas únicas
    turmas_pks = alocacoes.values_list('turma__pk', flat=True).distinct()
    
    # Filtra as turmas
    turmas_obj = Turma.objects.filter(pk__in=turmas_pks)
    turmas_ativas = turmas_obj.filter(status_aprovacao='Aprovada').count() # Assumindo status
    
    # Total de alunos *nessas* turmas
    total_alunos = Aluno.objects.filter(turma_atual__pk__in=turmas_pks, status_matricula='Ativo').count()

    context = {
        'titulo': 'Dashboard do Professor',
        'turmas_ativas': turmas_ativas,
        'total_alunos': total_alunos,
        'proximas_aulas': turmas_obj[:5], # Simplificado para as turmas
    }
    return render(request, 'dashboards/professor_dashboard.html', context)


# ---------------------------------------------------------------------
# 🧾 Dashboard da Secretaria (Atualizado)
# ---------------------------------------------------------------------
@role_required('secretaria')
def secretaria_dashboard_view(request):
    context = {
        'titulo': 'Dashboard da Secretaria',
        'total_alunos': Aluno.objects.count(),
        'matriculas_ativas': Aluno.objects.filter(status_matricula='Ativo').count(), # Corrigido
        'turmas_ativas': Turma.objects.filter(status_aprovacao='Aprovada').count(), # Corrigido
    }
    return render(request, 'dashboards/secretaria_dashboard.html', context)


# ---------------------------------------------------------------------
# 🧭 Dashboard da Coordenação (Atualizado)
# ---------------------------------------------------------------------
@role_required('coordenacao')
def coordenacao_dashboard_view(request):
    context = {
        'titulo': 'Dashboard da Coordenação',
        'total_turmas': Turma.objects.count(),
        'total_alunos': Aluno.objects.count(),
        'total_professores': Professor.objects.count(), # Corrigido
    }
    return render(request, 'dashboards/coordenacao_dashboard.html', context)

# #####################################################################
# APIs DA COORDENAÇÃO (ATUALIZADAS)
# #####################################################################

@role_required('coordenacao')
def api_coordenacao_kpis(request):
    """Retorna KPIs (ATUALIZADO para 'Historico')"""
    total_turmas = Turma.objects.count()
    professores_ativos = Professor.objects.filter(status_professor='Ativo').count()
    total_alunos = Aluno.objects.count()
    total_alunos_com_historico = Historico.objects.values('id_aluno').distinct().count() or 1
    
    # Alunos em risco: média < 7 OU frequência < 75%
    # (Baseado na lógica do seu boletim antigo)
    risco_count = Historico.objects.filter(
        Q(media_final__lt=7) | Q(frequencia_percentual__lt=75)
    ).values('id_aluno').distinct().count()
    
    risco_pct = f"{round((risco_count / total_alunos_com_historico) * 100, 1)}%"

    return JsonResponse({
        'total_turmas': total_turmas,
        'professores_ativos': professores_ativos,
        'total_alunos': total_alunos,
        'alunos_risco_pct': risco_pct,
    })


@role_required('coordenacao')
def api_coordenacao_desempenho(request):
    """Retorna desempenho médio por turma (ATUALIZADO para 'Historico')"""
    results = []
    turmas = Turma.objects.all().order_by('nome')
    for turma in turmas:
        # Média das médias finais do histórico para alunos dessa turma
        avg = Historico.objects.filter(
            turma_disciplina_professor__turma=turma
        ).aggregate(v=Avg('media_final'))['v']
        
        value = round(float(avg), 1) if avg is not None else None
        results.append({'codigo': turma.nome, 'valor': value}) # Usei turma.nome

    return JsonResponse({'results': results})


@role_required('coordenacao')
def api_coordenacao_aprovacao(request):
    """Retorna índices de aprovação (ATUALIZADO para 'Historico')"""
    
    # Contagem de alunos únicos por status no histórico
    aprovados = Historico.objects.filter(status_aprovacao='Aprovado').values('id_aluno').distinct().count()
    recuperacao = Historico.objects.filter(status_aprovacao='Recuperação').values('id_aluno').distinct().count()
    reprovados = Historico.objects.filter(status_aprovacao='Reprovado').values('id_aluno').distinct().count()

    total_avaliados = Historico.objects.values('id_aluno').distinct().count() or 1
    total_alunos = Aluno.objects.count()

    return JsonResponse({
        'total': total_alunos,
        'aprovados_pct': round((aprovados / total_avaliados) * 100),
        'recuperacao_pct': round((recuperacao / total_avaliados) * 100),
        'reprovados_pct': round((reprovados / total_avaliados) * 100),
    })


@role_required('coordenacao')
def api_coordenacao_atividades(request):
    """Atividades recentes (ATUALIZADO)"""
    items = []
    # Usando novos alunos
    recentes_alunos = Aluno.objects.order_by('-data_matricula')[:3]
    for a in recentes_alunos:
        items.append({
            'tipo': 'novo',
            'titulo': f'Novo aluno: {a.user.get_full_name()}',
            'detalhe': f'{a.RA_aluno} • há pouco',
            'badge': 'Novo'
        })
        
    if len(items) < 3:
        items.extend([
            {'tipo': 'aprovado', 'titulo': 'Turma TI-2023A Aprovada', 'detalhe': 'Coord. Maria • há 2 horas', 'badge': 'Aprovado'},
            {'tipo': 'atencao', 'titulo': 'Frequência baixa detectada na Turma ELE-2023B', 'detalhe': 'Sistema • há 6 horas', 'badge': 'Atenção'},
        ])

    return JsonResponse({'results': items[:3]})


# ---------------------------------------------------------------------
# 🔧 Páginas da Secretaria (ATUALIZADO)
# ---------------------------------------------------------------------
@login_required
@user_passes_test(is_secretaria) # Adicionada permissão
def gestao_alunos_view(request):
    # Contexto mínimo (usado nos cards)
    total_alunos = Aluno.objects.count()
    matriculas_ativas = Aluno.objects.filter(status_matricula='Ativo').count()

    return render(request, 'dashboards/gestao_alunos.html', {
        'total_alunos': total_alunos,
        'matriculas_ativas': matriculas_ativas,
    })

# (As views abaixo foram mantidas, mas com permissão adicionada)

@login_required
@user_passes_test(is_secretaria)
def controle_financeiro_view(request):
    context = {'titulo': 'Controle Financeiro'}
    return render(request, 'dashboards/controle_financeiro.html', context)


@login_required
@user_passes_test(is_secretaria)
def gestao_documentos_view(request):
    context = {'titulo': 'Gestão de Documentos'}
    return render(request, 'dashboards/gestao_documentos.html', context)


@login_required
@user_passes_test(is_secretaria)
def comunicacao_secretaria_view(request):
    context = {'titulo': 'Comunicação - Secretaria'}
    return render(request, 'dashboards/comunicacao_secretaria.html', context)


@login_required
def perfil_view(request):
    return render(request, 'not_implemented.html', {'title': 'Meu Perfil'})


# ---------------------------------------------------------------------
# 📊 Boletim (Aluno) (ATUALIZADO)
# ---------------------------------------------------------------------
@role_required('aluno')
def boletim_view(request):
    try:
        aluno = Aluno.objects.get(user=request.user)
    except Aluno.DoesNotExist:
        messages.error(request, "Perfil de Aluno não encontrado.")
        return redirect('home')

    # A lógica de boletim agora vem direto do 'Historico'
    boletim = Historico.objects.filter(id_aluno=aluno).order_by(
        'periodo_realizacao', 'turma_disciplina_professor__disciplina__nome'
    ).select_related('turma_disciplina_professor__disciplina', 'turma_disciplina_professor__turma')

    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="boletim_{aluno.RA_aluno}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Período', 'Disciplina', 'Turma', 'Média Final', 'Faltas', 'Frequência (%)', 'Status'])
        for b in boletim:
            writer.writerow([
                b.periodo_realizacao,
                b.turma_disciplina_professor.disciplina.nome,
                b.turma_disciplina_professor.turma.nome,
                b.media_final or '',
                b.total_faltas or '',
                b.frequencia_percentual or '',
                b.status_aprovacao or '',
            ])
        return response

    context = {
        'titulo': 'Boletim Escolar',
        'aluno': aluno,
        'boletim': boletim,
    }
    return render(request, 'dashboards/boletim.html', context)


# ---------------------------------------------------------------------
# 📅 Avisos e Eventos (Aluno) (Mantido)
# ---------------------------------------------------------------------
@role_required('aluno')
def avisos_eventos_view(request):
    avisos = [
        {'titulo': 'Manutenção no Portal', 'tipo': 'Informativo', 'mensagem': 'O portal ficará fora do ar para manutenção nesta sexta-feira, das 22h às 02h.', 'data': '2025-11-12'},
    ]
    eventos = [
        {'titulo': 'Feira de Projetos', 'data': '2025-12-05', 'hora_inicio': '09:00', 'hora_fim': '18:00', 'local': 'Pátio Central'},
    ]
    return render(request, 'dashboards/avisos_eventos.html', {'titulo': 'Avisos e Eventos', 'avisos': avisos, 'eventos': eventos})


# =====================================================================
# COORDENAÇÃO - PÁGINAS INTERATIVAS (ATUALIZADO)
# =====================================================================

@role_required('coordenacao')
def coordenacao_desempenho_view(request):
    """Página de Desempenho Acadêmico para Coordenador"""
    turmas = Turma.objects.all()
    context = {
        'titulo': 'Desempenho Acadêmico',
        'turmas': turmas,
    }
    return render(request, 'dashboards/coordenacao_desempenho.html', context)


@role_required('coordenacao')
def coordenacao_gestao_view(request):
    """Página de Gestão para Coordenador"""
    total_alunos = Aluno.objects.count()
    alunos_ativos = Aluno.objects.filter(status_matricula='Ativo').count() # Corrigido
    turmas = Turma.objects.all()
    context = {
        'titulo': 'Gestão Acadêmica',
        'total_alunos': total_alunos,
        'alunos_ativos': alunos_ativos,
        'turmas': turmas,
    }
    return render(request, 'dashboards/coordenacao_gestao.html', context)


@role_required('coordenacao')
def coordenacao_comunicacao_view(request):
    """Página de Comunicação para Coordenador"""
    context = {'titulo': 'Comunicação'}
    return render(request, 'dashboards/coordenacao_comunicacao.html', context)


@role_required('coordenacao')
def coordenacao_relatorios_view(request):
    """Página de Relatórios para Coordenador"""
    context = {'titulo': 'Relatórios da Unidade'}
    return render(request, 'dashboards/coordenacao_relatorios.html', context)