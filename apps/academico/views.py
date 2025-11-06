from django.shortcuts import render, redirect

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import AlunoForm, AlunoEditForm
from .models import Aluno, Matricula

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
