import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User

# Imports dos seus modelos
from apps.academico.models import (
    Turma, Aluno, Professor, Secretaria, Coordenacao, 
    Historico, Curso, TurmaDisciplinaProfessor, Disciplina
)
from apps.usuarios.models import Profile

# Se você tiver um model de Material, mantenha. Se não, pode comentar esta linha.
# from .models import Material 


# =============================================================================
# 1. DECORATORS E AUXILIARES DE PERMISSÃO
# =============================================================================

def isaluno(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'aluno'

def isprofessor(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'professor'

def issecretaria(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'secretaria'

def iscoordenacao(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.tipo == 'coordenacao'

def rolerequired(*roles):
    """
    Decorator personalizado para verificar se o usuário tem um dos perfis exigidos.
    Uso: @rolerequired("aluno", "professor")
    """
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            userroles = []
            if isaluno(request.user): userroles.append("aluno")
            if isprofessor(request.user): userroles.append("professor")
            if issecretaria(request.user): userroles.append("secretaria")
            if iscoordenacao(request.user): userroles.append("coordenacao")
            
            # Se for superuser, permite acesso (opcional, útil para debug)
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if not any(role in userroles for role in roles):
                messages.error(request, "Acesso negado a esta área.")
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# 2. VIEW PRINCIPAL (ROTEAMENTO INTELIGENTE)
# =============================================================================

@login_required
def home(request):
    """
    Redireciona o usuário para o dashboard correto com base no perfil.
    """
    if isaluno(request.user): return redirect('aluno_dashboard')
    elif isprofessor(request.user): return redirect('professor_dashboard')
    elif issecretaria(request.user): return redirect('secretaria_dashboard')
    elif iscoordenacao(request.user): return redirect('coordenacao_dashboard')
    
    # Se não tiver perfil definido, mostra uma home genérica ou erro
    return render(request, "home.html")


# =============================================================================
# 3. DASHBOARD DO PROFESSOR (FUNCIONAL)
# =============================================================================

@rolerequired("professor")
def professor_dashboard_view(request):
    context = {}
    try:
        # Tenta buscar o objeto Professor ligado ao User
        professor = Professor.objects.select_related('user').get(user=request.user)
        context['professor'] = professor
    except Professor.DoesNotExist:
        context['professor'] = None
        # Se não for professor "oficial" (ex: admin logado), renderiza vazio para evitar erro 500
        return render(request, "dashboards/professor_dashboard.html", context)

    # --- 1. KPIs Principais ---
    # Buscamos as alocações deste professor (Qual Turma + Qual Disciplina ele dá aula)
    alocacoes = TurmaDisciplinaProfessor.objects.filter(professor=professor).select_related('turma', 'disciplina')
    
    # Total de turmas distintas
    total_turmas = alocacoes.values('turma').distinct().count()
    
    # Total de alunos (alunos matriculados nas turmas onde ele dá aula)
    turmas_ids = alocacoes.values_list('turma_id', flat=True)
    total_alunos = Aluno.objects.filter(turma_atual__id__in=turmas_ids).distinct().count()
    
    # Pendências (Exemplo: Turmas pendentes de aprovação ou diários não fechados)
    pendencias_count = Turma.objects.filter(id__in=turmas_ids, status_aprovacao='Pendente').count()

    # --- 2. Alunos em Risco (Nota < 6 ou Freq < 75%) ---
    # Filtramos históricos de alunos APENAS nas matérias desse professor
    alunos_risco_qs = Historico.objects.filter(
        turma_disciplina_professor__professor=professor
    ).filter(
        Q(media_final__lt=6.0) | Q(frequencia_percentual__lt=75.0)
    ).select_related('id_aluno__user', 'turma_disciplina_professor__disciplina').order_by('media_final')[:5]

    alunos_risco = []
    for h in alunos_risco_qs:
        motivo = []
        if h.media_final is not None and h.media_final < 6.0:
            motivo.append(f"Nota: {h.media_final}")
        if h.frequencia_percentual is not None and h.frequencia_percentual < 75.0:
            motivo.append(f"Freq: {h.frequencia_percentual}%")
            
        alunos_risco.append({
            'nome': h.id_aluno.user.get_full_name(),
            'disciplina': h.turma_disciplina_professor.disciplina.nome,
            'motivo': " | ".join(motivo),
            'classe_css': 'text-danger' if 'Freq' in (motivo[0] if motivo else '') else 'text-warning'
        })

    # --- 3. Gráfico: Média de Notas por Turma ---
    grafico_qs = Historico.objects.filter(
        turma_disciplina_professor__professor=professor
    ).values('turma_disciplina_professor__turma__nome').annotate(
        media_turma=Avg('media_final')
    ).order_by('turma_disciplina_professor__turma__nome')

    chart_labels = [item['turma_disciplina_professor__turma__nome'] for item in grafico_qs]
    chart_data = [round(item['media_turma'] or 0, 1) for item in grafico_qs]

    # Dados fake se não houver histórico (para o gráfico não ficar vazio no início)
    if not chart_labels:
        chart_labels = ["Sem dados"]
        chart_data = [0]

    dashboard_data = {
        'labels': chart_labels,
        'data': chart_data
    }

    # Contexto final
    context.update({
        'total_turmas': total_turmas,
        'total_alunos': total_alunos,
        'pendencias': pendencias_count,
        'alunos_risco': alunos_risco,
        'dashboard_data_json': json.dumps(dashboard_data, cls=DjangoJSONEncoder),
        # Pega a primeira turma como "Destaque" se existir
        'turma_destaque': alocacoes.first().turma if alocacoes.exists() else None
    })

    return render(request, "dashboards/professor_dashboard.html", context)


# =============================================================================
# 4. DASHBOARD DA SECRETARIA
# =============================================================================

@rolerequired("secretaria")
def secretaria_dashboard_view(request):
    context = {}
    try:
        secretaria = Secretaria.objects.select_related('user').get(user=request.user)
        context['secretaria'] = secretaria
    except Secretaria.DoesNotExist:
        context['secretaria'] = None
    
    # KPIs simples
    context.update({
        'total_alunos': Aluno.objects.count(),
        'total_turmas': Turma.objects.count(),
        'total_cursos': Curso.objects.count(),
        # Exemplo de cálculo de inadimplência ou pendências
        'matriculas_ativas': Aluno.objects.filter(status_matricula='Ativo').count()
    })
    return render(request, "dashboards/secretaria_dashboard.html", context)


# =============================================================================
# 5. DASHBOARD DA COORDENAÇÃO (VISÃO GERAL)
# =============================================================================

@rolerequired("coordenacao")
def coordenacao_dashboard_view(request):
    context = {}
    try:
        coordenacao = Coordenacao.objects.select_related('user').get(user=request.user)
        context['coordenacao'] = coordenacao
    except Coordenacao.DoesNotExist:
        context['coordenacao'] = None
    
    # KPIs
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.filter(status_professor='Ativo').count()
    total_turmas = Turma.objects.count()
    
    alunos_risco_count = Historico.objects.filter(
        Q(media_final__lt=6.0) | Q(frequencia_percentual__lt=75.0)
    ).values('id_aluno').distinct().count()

    # Gráfico Dispersão
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

    # Gráfico Eficiência por Curso
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

    # Atividades Recentes
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
# 6. DASHBOARD DO ALUNO
# =============================================================================

@rolerequired("aluno")
def aluno_dashboard_view(request):
    context = {}
    try:
        aluno = Aluno.objects.select_related('user', 'turma_atual').get(user=request.user)
        context['aluno'] = aluno
    except Aluno.DoesNotExist:
        context['aluno'] = None
    return render(request, "dashboards/aluno_dashboard.html", context)


# =============================================================================
# 7. SUB-PÁGINAS E FUNCIONALIDADES ESPECÍFICAS
# =============================================================================

# --- COORDENAÇÃO ---

@rolerequired("coordenacao")
def coordenacao_desempenho_view(request):
    context = {}
    # Lógica de desempenho (simplificada para o exemplo)
    alunos_list = []
    # (Pode-se copiar a lógica detalhada anterior se desejar, ou manter simples para carregar a página)
    desempenho_data = {
        'alunos': [],
        'turmas': [],
        'grafico_notas': {'Aprovado': 0, 'Recuperação': 0, 'Reprovado': 0},
        'grafico_frequencia': {'labels': [], 'data': []}
    }
    context['desempenho_data_json'] = json.dumps(desempenho_data)
    return render(request, "dashboards/coordenacao_desempenho.html", context)

@rolerequired("coordenacao")
def coordenacao_gestao_view(request):
    # Busca dados para o CRUD da coordenação
    alunos_list = [{
        'id': a.pk,
        'nome': a.user.get_full_name(),
        'matricula': a.RA_aluno,
        'turma': a.turma_atual.nome if a.turma_atual else 'Sem turma',
        'status': a.status_matricula
    } for a in Aluno.objects.select_related('user', 'turma_atual').all()]

    turmas_list = [{
        'id': t.pk, 'codigo': t.nome, 
        'nome': t.id_curso.nome_curso if t.id_curso else '',
        'vagas': t.capacidade_maxima
    } for t in Turma.objects.all()]

    profs_list = [{
        'id': p.pk, 'nome': p.user.get_full_name(), 'email': p.user.email
    } for p in Professor.objects.select_related('user').all()]

    discs_list = [{
        'id': d.pk, 'codigo': d.cod_disciplina, 'nome': d.nome
    } for d in Disciplina.objects.all()]

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


# --- SECRETARIA ---

@rolerequired("secretaria")
def gestao_alunos_view(request):
    alunos = Aluno.objects.select_related('user', 'turma_atual').all()
    # Adicionar KPIs específicos desta tela se necessário
    context = {
        'alunos': alunos,
        'total_alunos': alunos.count(),
        'matriculas_ativas': alunos.filter(status_matricula__iexact='Ativo').count()
    }
    return render(request, "dashboards/gestao_alunos.html", context)

@rolerequired("secretaria")
def gestao_documentos_view(request):
    return render(request, "dashboards/gestao_documentos.html")

@rolerequired("secretaria")
def controle_financeiro_view(request):
    return render(request, "dashboards/controle_financeiro.html")

@rolerequired("secretaria")
def comunicacao_secretaria_view(request):
    return render(request, "dashboards/comunicacao_secretaria.html")


# --- ALUNO ---

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


# --- GERAL ---

@login_required
def perfil_view(request):
    return render(request, "dashboards/perfil.html")


# =============================================================================
# 8. API VIEWS (AJAX/JSON)
# =============================================================================

@require_http_methods(["POST"])
# Pode ajustar a permissão para aceitar "secretaria" também
@login_required 
def save_aluno_view(request):
    try:
        # Verifica permissão manualmente se quiser flexibilidade
        if not (issecretaria(request.user) or iscoordenacao(request.user)):
             return JsonResponse({'success': False, 'message': 'Sem permissão.'}, status=403)

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
            
            # Valores padrão para criação rápida
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
@login_required
def delete_aluno_view(request, pk):
    try:
        if not (issecretaria(request.user) or iscoordenacao(request.user)):
             return JsonResponse({'success': False, 'message': 'Sem permissão.'}, status=403)

        aluno = Aluno.objects.get(pk=pk)
        user = aluno.user
        aluno.delete()
        user.delete()
        return JsonResponse({'success': True, 'message': 'Aluno excluído com sucesso!'})
    except Aluno.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Aluno não encontrado.'}, status=404)


# =============================================================================
# 9. PLACEHOLDER APIs (Para evitar erro 404 em chamadas JS antigas)
# =============================================================================

@login_required
def api_coordenacao_kpis(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_desempenho(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_aprovacao(request): return JsonResponse({'status': 'ok'})
@login_required
def api_coordenacao_atividades(request): return JsonResponse({'status': 'ok'})