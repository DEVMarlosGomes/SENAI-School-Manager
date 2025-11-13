from django.shortcuts import render, redirect

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import AlunoForm, AlunoEditForm
from .models import Aluno, Matricula
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.forms.models import model_to_dict
import json

def is_secretaria(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_secretaria

@login_required
@user_passes_test(is_secretaria)
def lista_alunos_view(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    alunos = Aluno.objects.all()
    
    if search_query:
        alunos = alunos.filter(
            Q(matricula__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__profile__cpf__icontains=search_query)
        )
    
    if status_filter:
        alunos = alunos.filter(matricula__status=status_filter)
    
    paginator = Paginator(alunos.order_by('user__first_name'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_alunos': Aluno.objects.count(),
        'ativos': Matricula.objects.filter(status='ativa').count(),
    }
    return render(request, 'academico/lista_alunos.html', context)

@login_required
@user_passes_test(is_secretaria)
def detalhe_aluno_view(request, pk):
    aluno = Aluno.objects.get(pk=pk)
    matriculas = aluno.matriculas.all().order_by('-data_matricula')
    notas = []
    for matricula in matriculas:
        notas.extend(list(matricula.nota_set.all().order_by('-data')))
    
    context = {
        'aluno': aluno,
        'matriculas': matriculas,
        'notas': notas[:10],  # Últimas 10 notas
        'faltas': aluno.matriculas.first().frequencia_set.filter(presenca=False).count() if aluno.matriculas.exists() else 0
    }
    return render(request, 'academico/detalhe_aluno.html', context)

@login_required
@user_passes_test(is_secretaria)
def editar_aluno_view(request, pk):
    aluno = Aluno.objects.get(pk=pk)
    if request.method == 'POST':
        form = AlunoEditForm(request.POST, instance=aluno.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados do aluno atualizados com sucesso!')
            return redirect('detalhe_aluno', pk=pk)
    else:
        form = AlunoEditForm(instance=aluno.user)
    
    return render(request, 'academico/editar_aluno.html', {'form': form, 'aluno': aluno})

@login_required
@user_passes_test(is_secretaria)
def cadastro_aluno_view(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aluno cadastrado com sucesso!')
            return redirect('secretaria_dashboard')
    else:
        form = AlunoForm()
    return render(request, 'academico/cadastro_aluno.html', {'form': form})


@login_required
@user_passes_test(is_secretaria)
@require_http_methods(['GET', 'POST'])
def api_alunos(request):
    """GET -> lista alunos (JSON). POST -> cria novo aluno a partir do AlunoForm (JSON).
    """
    if request.method == 'GET':
        alunos = Aluno.objects.select_related('user').all()
        data = []
        for a in alunos:
            nome = a.user.get_full_name() or a.user.first_name or ''
            primeira_matricula = a.matriculas.first()
            status = primeira_matricula.status if primeira_matricula else ''
            curso = primeira_matricula.turma.curso.nome if primeira_matricula and primeira_matricula.turma and primeira_matricula.turma.curso else ''
            data.append({
                'id': a.id,
                'nome': nome,
                'matricula': a.matricula,
                'status': status,
                'curso': curso,
            })
        return JsonResponse({'results': data})

    # POST -> criar aluno
    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponseBadRequest('JSON inválido')

        # Mapear dados para o AlunoForm
        form_data = {
            'username': payload.get('username') or payload.get('matricula') or '',
            'first_name': payload.get('first_name', ''),
            'last_name': payload.get('last_name', ''),
            'email': payload.get('email', ''),
            'password1': payload.get('password') or 'ChangeMe123!',
            'password2': payload.get('password') or 'ChangeMe123!',
            'cpf': payload.get('cpf', ''),
            'telefone': payload.get('telefone', ''),
            'data_nascimento': payload.get('data_nascimento', ''),
            'endereco': payload.get('endereco', ''),
        }

        form = AlunoForm(form_data)
        if form.is_valid():
            user = form.save()
            aluno = Aluno.objects.get(user=user)
            nome = user.get_full_name() or user.first_name
            return JsonResponse({'id': aluno.id, 'nome': nome, 'matricula': aluno.matricula})
        else:
            return JsonResponse({'errors': form.errors}, status=400)


@login_required
@user_passes_test(is_secretaria)
@require_http_methods(['GET', 'PUT', 'DELETE'])
def api_aluno_detail(request, pk):
    try:
        aluno = Aluno.objects.select_related('user').get(pk=pk)
    except Aluno.DoesNotExist:
        return JsonResponse({'error': 'Aluno não encontrado'}, status=404)

    if request.method == 'GET':
        user = aluno.user
        data = {
            'id': aluno.id,
            'matricula': aluno.matricula,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return JsonResponse(data)

    if request.method == 'PUT':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponseBadRequest('JSON inválido')
        user = aluno.user
        user.first_name = payload.get('first_name', user.first_name)
        user.last_name = payload.get('last_name', user.last_name)
        user.email = payload.get('email', user.email)
        user.save()
        # Atualizar status/turma da matrícula quando fornecido
        status = payload.get('status')
        turma_codigo = payload.get('turma_codigo') or payload.get('turma')
        if status or turma_codigo:
            # Tentar obter a matrícula principal (a primeira) ou criar uma se não existir
            matricula = aluno.matriculas.first()
            from .models import Turma
            if turma_codigo:
                try:
                    # tentar por id
                    turma = None
                    if isinstance(turma_codigo, int) or (isinstance(turma_codigo, str) and turma_codigo.isdigit()):
                        turma = Turma.objects.filter(id=int(turma_codigo)).first()
                    if not turma:
                        turma = Turma.objects.filter(codigo__iexact=str(turma_codigo)).first()
                    if turma:
                        if matricula:
                            matricula.turma = turma
                            matricula.save()
                        else:
                            matricula = Matricula.objects.create(aluno=aluno, turma=turma, status=status or 'ativa')
                except Exception:
                    # ignorar falhas de resolução de turma
                    pass
            if status and matricula:
                matricula.status = status
                matricula.save()

        return JsonResponse({'status': 'ok'})

    if request.method == 'DELETE':
        aluno.user.delete()
        return JsonResponse({'status': 'deleted'})
