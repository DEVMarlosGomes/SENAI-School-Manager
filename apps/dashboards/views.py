from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
from datetime import date
import json
import csv

from apps.academico.models import Turma, Aluno, Matricula, Nota, Frequencia
from .models import Material

# ---------------------------------------------------------------------
# 🔒 Decorator personalizado para restringir acesso por tipo de usuário
# ---------------------------------------------------------------------
def role_required(*roles):
    """Decorator para restringir acesso por tipo de perfil."""
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                messages.error(request, "Perfil de usuário não configurado.")
                return redirect('home')

            if request.user.profile.tipo not in roles:
                messages.error(request, "Acesso negado a esta área.")
                return redirect('redirecionar_dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------
# 🌐 Home
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# 🎓 Dashboard do Aluno
# ---------------------------------------------------------------------
@role_required('aluno')
def aluno_dashboard_view(request):
    context = {
        'titulo': 'Dashboard do Aluno',
        'notas_recentes': Nota.objects.filter(
            matricula__aluno__user=request.user
        ).order_by('-data')[:5],
        'faltas_recentes': Frequencia.objects.filter(
            matricula__aluno__user=request.user, presenca=False
        ).order_by('-data')[:5],
        'proximas_aulas': [
            {'disciplina': 'Automação Industrial II', 'professor': 'Maria Silva', 'horario': '19:00', 'sala': 'Lab 3'},
            {'disciplina': 'Programação Web', 'professor': 'João Santos', 'horario': '20:45', 'sala': 'Lab 1'},
        ],
        'avisos': [
            {'titulo': 'Alteração no Cronograma', 'tipo': 'Urgente', 'mensagem': 'As aulas de programação foram remanejadas para terça-feira.', 'data': '2025-11-10'},
            {'titulo': 'Palestra sobre Indústria 4.0', 'tipo': 'Importante', 'mensagem': 'Convidamos todos os alunos para a palestra sobre Indústria 4.0.', 'data': '2025-11-09'},
        ],
        'eventos': [
            {'titulo': 'Workshop de Inovação', 'data': date(2025, 11, 25), 'hora_inicio': '14:00', 'hora_fim': '17:00', 'local': 'Auditório Principal'},
            {'titulo': 'Feira de Projetos', 'data': date(2025, 12, 5), 'hora_inicio': '09:00', 'hora_fim': '18:00', 'local': 'Pátio Central'},
        ],
    }
    return render(request, 'dashboards/aluno_dashboard.html', context)


# ---------------------------------------------------------------------
# 📚 Materiais de Estudo
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
# 🗓️ Calendário (Aluno)
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
# 👩‍🏫 Dashboard do Professor
# ---------------------------------------------------------------------
@role_required('professor')
def professor_dashboard_view(request):
    context = {
        'titulo': 'Dashboard do Professor',
        'turmas_ativas': Turma.objects.filter(professor=request.user, ativa=True).count(),
        'total_alunos': Matricula.objects.filter(turma__professor=request.user, status='ativa').count(),
        'proximas_aulas': Turma.objects.filter(professor=request.user, ativa=True)[:5],
    }
    return render(request, 'dashboards/professor_dashboard.html', context)


# ---------------------------------------------------------------------
# 🧾 Dashboard da Secretaria
# ---------------------------------------------------------------------
@role_required('secretaria')
def secretaria_dashboard_view(request):
    context = {
        'titulo': 'Dashboard da Secretaria',
        'total_alunos': Aluno.objects.count(),
        'matriculas_ativas': Matricula.objects.filter(status='ativa').count(),
        'turmas_ativas': Turma.objects.filter(ativa=True).count(),
    }
    return render(request, 'dashboards/secretaria_dashboard.html', context)


# ---------------------------------------------------------------------
# 🧭 Dashboard da Coordenação
# ---------------------------------------------------------------------
@role_required('coordenacao')
def coordenacao_dashboard_view(request):
    context = {
        'titulo': 'Dashboard da Coordenação',
        'total_turmas': Turma.objects.count(),
        'total_alunos': Aluno.objects.count(),
        'total_professores': Turma.objects.values('professor').distinct().count(),
    }
    return render(request, 'dashboards/coordenacao_dashboard.html', context)


# ---------------------------------------------------------------------
# 🔧 Placeholders (em construção)
# ---------------------------------------------------------------------
@login_required
def gestao_alunos_view(request):
    return render(request, 'not_implemented.html', {'title': 'Gestão de Alunos'})

@login_required
def controle_financeiro_view(request):
    return render(request, 'not_implemented.html', {'title': 'Controle Financeiro'})

@login_required
def gestao_documentos_view(request):
    return render(request, 'not_implemented.html', {'title': 'Gestão de Documentos'})

@login_required
def comunicacao_secretaria_view(request):
    return render(request, 'not_implemented.html', {'title': 'Comunicação - Secretaria'})

@login_required
def perfil_view(request):
    return render(request, 'not_implemented.html', {'title': 'Meu Perfil'})


# ---------------------------------------------------------------------
# 📊 Boletim (Aluno)
# ---------------------------------------------------------------------
@role_required('aluno')
def boletim_view(request):
    try:
        aluno = Aluno.objects.get(user=request.user)
    except Aluno.DoesNotExist:
        return render(request, 'not_implemented.html', {'title': 'Boletim', 'message': 'Usuário não é um aluno.'})

    matriculas = Matricula.objects.filter(aluno=aluno).order_by('-data_matricula')

    boletim = []
    for m in matriculas:
        notas_qs = Nota.objects.filter(matricula=m)
        notas_vals = [float(n.valor) for n in notas_qs]
        media = round(sum(notas_vals)/len(notas_vals), 1) if notas_vals else None

        total_sessions = Frequencia.objects.filter(matricula=m).count()
        faltas = Frequencia.objects.filter(matricula=m, presenca=False).count()
        frequencia_pct = round(((total_sessions - faltas) / total_sessions) * 100, 1) if total_sessions > 0 else None

        if media is None:
            status = 'Sem notas'
        elif frequencia_pct is None:
            status = 'Sem frequência'
        elif media >= 7 and frequencia_pct >= 75:
            status = 'Aprovado'
        elif media < 7 and frequencia_pct >= 75:
            status = 'Recuperação'
        else:
            status = 'Reprovado'

        boletim.append({
            'matricula': m,
            'turma': m.turma,
            'curso': m.turma.curso if m.turma else None,
            'notas': notas_qs,
            'media': media,
            'faltas': faltas,
            'frequencia': frequencia_pct,
            'status': status,
        })

    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="boletim_{aluno.matricula}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Matrícula', 'Turma', 'Curso', 'Média', 'Faltas', 'Frequência (%)', 'Status'])
        for b in boletim:
            writer.writerow([
                aluno.matricula,
                b['turma'].codigo if b['turma'] else '',
                b['curso'].nome if b['curso'] else '',
                b['media'] or '',
                b['faltas'],
                b['frequencia'] or '',
                b['status'],
            ])
        return response

    context = {
        'titulo': 'Boletim Escolar',
        'aluno': aluno,
        'boletim': boletim,
    }
    return render(request, 'dashboards/boletim.html', context)


# ---------------------------------------------------------------------
# 📅 Avisos e Eventos (Aluno)
# ---------------------------------------------------------------------
@role_required('aluno')
def avisos_eventos_view(request):
    avisos = [
        {'titulo': 'Manutenção no Portal', 'tipo': 'Informativo', 'mensagem': 'O portal ficará fora do ar para manutenção nesta sexta-feira, das 22h às 02h.', 'data': '2025-11-12'},
        {'titulo': 'Bolsa de Estudo', 'tipo': 'Importante', 'mensagem': 'Inscrições abertas para bolsas até 20/11.', 'data': '2025-11-05'},
    ]
    eventos = [
        {'titulo': 'Feira de Projetos', 'data': '2025-12-05', 'hora_inicio': '09:00', 'hora_fim': '18:00', 'local': 'Pátio Central'},
        {'titulo': 'Palestra Indústria 4.0', 'data': '2025-11-25', 'hora_inicio': '14:00', 'hora_fim': '16:00', 'local': 'Auditório Principal'},
    ]
    return render(request, 'dashboards/avisos_eventos.html', {'titulo': 'Avisos e Eventos', 'avisos': avisos, 'eventos': eventos})
