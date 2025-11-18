from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
import json
import requests  # ← ADICIONADO: Para a API ViaCEP


from .forms import AlunoForm, AlunoEditForm
from .models import Aluno, Historico, Secretaria, Turma # Importações corrigidas


# #############################################################################
# FUNÇÃO DE VERIFICAÇÃO DE PERMISSÃO (ATUALIZADA)
# #############################################################################
def is_secretaria(user):
    """
    Verifica se o usuário é uma 'Secretaria' usando o NOVO modelo
    (apps.academico.models.Secretaria) em vez do 'Profile' antigo.
    """
    return user.is_authenticated and Secretaria.objects.filter(user=user).exists()


# #############################################################################
# VIEWS ATUALIZADAS (COMPATÍVEIS COM OS NOVOS MODELOS)
# #############################################################################


@login_required
@user_passes_test(is_secretaria)
def lista_alunos_view(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Usando o novo modelo Aluno
    alunos = Aluno.objects.all()
    
    if search_query:
        alunos = alunos.filter(
            Q(RA_aluno__icontains=search_query) |            # Corrigido: de 'matricula' para 'RA_aluno'
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
            # Nota: A busca por CPF estava no 'Profile' antigo e foi removida.
            # Se o CPF for essencial, ele deve ser adicionado ao modelo 'Aluno'.
        )
    
    if status_filter:
        alunos = alunos.filter(status_matricula=status_filter) # Corrigido: 'matricula__status' para 'status_matricula'
    
    paginator = Paginator(alunos.order_by('user__first_name'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_alunos': Aluno.objects.count(),
        'ativos': Aluno.objects.filter(status_matricula='Ativo').count(), # Corrigido: Usa 'Aluno'
    }
    return render(request, 'academico/lista_alunos.html', context)


@login_required
@user_passes_test(is_secretaria)
def detalhe_aluno_view(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    
    # Lógica de Matrícula, Nota e Frequência foi substituída por 'Historico'
    historico = aluno.historico.all().order_by('-periodo_realizacao')
    
    # Lógica de faltas agora vem do 'Historico'
    agregado = aluno.historico.aggregate(total_faltas=Sum('total_faltas'))
    total_faltas = agregado['total_faltas'] or 0
    
    context = {
        'aluno': aluno,
        'historico': historico,  # 'matriculas' e 'notas' combinadas
        'total_faltas': total_faltas
    }
    return render(request, 'academico/detalhe_aluno.html', context)


@login_required
@user_passes_test(is_secretaria)
def editar_aluno_view(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == 'POST':
        # O 'instance' do form é 'aluno', não 'aluno.user'
        form = AlunoEditForm(request.POST, instance=aluno)
        if form.is_valid():
            # O form (AlunoEditForm) foi desenhado para ter os campos do User
            # Precisamos salvar o User e o Aluno separadamente
            
            # 1. Salva o Aluno (mas não o User ainda)
            aluno_inst = form.save(commit=False)
            
            # 2. Atualiza o User manualmente
            user = aluno_inst.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            # 3. Salva o Aluno
            aluno_inst.save()
            
            messages.success(request, 'Dados do aluno atualizados com sucesso!')
            return redirect('detalhe_aluno', pk=pk)
    else:
        # O form __init__ que eu criei vai pré-popular os campos do User
        form = AlunoEditForm(instance=aluno)
    
    return render(request, 'academico/editar_aluno.html', {'form': form, 'aluno': aluno})


@login_required
@user_passes_test(is_secretaria)
def cadastro_aluno_view(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            # 1. Criar o User primeiro
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )
            except Exception as e:
                messages.error(request, f"Erro ao criar usuário: {e}")
                return render(request, 'academico/cadastro_aluno.html', {'form': form})
            
            # 2. Criar o Aluno e ligar ao User
            # (O form AlunoForm é um ModelForm de Aluno)
            aluno = form.save(commit=False)
            aluno.user = user  # Liga o aluno ao usuário criado
            aluno.pk = user.pk  # Usa o mesmo PK (necessário para OneToOneField com primary_key=True)
            aluno.save()
            
            messages.success(request, 'Aluno cadastrado com sucesso!')
            # Você precisa ter uma URL chamada 'secretaria_dashboard' no seu urls.py
            return redirect('lista_alunos_view') # Redirecionando para a lista
    else:
        form = AlunoForm()
    return render(request, 'academico/cadastro_aluno.html', {'form': form})



# #############################################################################
# API VIEWS (ATUALIZADAS)
# #############################################################################


@login_required
@user_passes_test(is_secretaria)
@require_http_methods(['GET', 'POST'])
def api_alunos(request):
    """ GET -> lista alunos (JSON). POST -> cria novo aluno (JSON). """
    
    if request.method == 'GET':
        alunos = Aluno.objects.select_related('user', 'turma_atual__id_curso').all()
        data = []
        for a in alunos:
            nome = a.user.get_full_name() or a.user.first_name or ''
            
            # Lógica de Matrícula removida
            status = a.status_matricula
            curso = a.turma_atual.id_curso.nome_curso if a.turma_atual and a.turma_atual.id_curso else ''
            
            data.append({
                'id': a.pk,
                'nome': nome,
                'matricula': a.RA_aluno, # Corrigido para RA_aluno
                'status': status,
                'curso': curso,
            })
        return JsonResponse({'results': data})


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
            'password': payload.get('password') or 'ChangeMe123!', # 'password1' e 'password2' não são campos do AlunoForm
            'RA_aluno': payload.get('matricula') or '', # Mapeado para RA_aluno
            'RG_aluno': payload.get('rg', ''),
            'data_nascimento': payload.get('data_nascimento', ''),
            'genero': payload.get('genero', ''),
            'estado_civil': payload.get('estado_civil', ''),
            # Adicionar outros campos do AlunoForm se necessário...
        }


        form = AlunoForm(form_data)
        if form.is_valid():
            # Lógica de criação de user + aluno
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )
                aluno = form.save(commit=False)
                aluno.user = user
                aluno.pk = user.pk
                aluno.save()
                
                nome = user.get_full_name() or user.first_name
                return JsonResponse({'id': aluno.pk, 'nome': nome, 'matricula': aluno.RA_aluno})
            except Exception as e:
                 return JsonResponse({'errors': str(e)}, status=400)
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
            'id': aluno.pk,
            'matricula': aluno.RA_aluno, # Corrigido para RA_aluno
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'status': aluno.status_matricula, # Corrigido
            'turma_id': aluno.turma_atual.pk if aluno.turma_atual else None
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
        
        # Atualizar Aluno (status e turma)
        aluno.status_matricula = payload.get('status', aluno.status_matricula)
        turma_id = payload.get('turma_id') or payload.get('turma')
        
        if turma_id:
            try:
                turma = Turma.objects.get(pk=int(turma_id))
                aluno.turma_atual = turma
            except Turma.DoesNotExist:
                pass # Ignora se a turma não for encontrada
            except (ValueError, TypeError):
                pass # Ignora se o ID for inválido
        
        aluno.save()
        return JsonResponse({'status': 'ok'})


    if request.method == 'DELETE':
        aluno.user.delete() # Apagar o User apaga o Aluno (on_delete=models.CASCADE)
        return JsonResponse({'status': 'deleted'})


# #############################################################################
# API EXTERNA - VIACEP (NOVA)
# #############################################################################


@require_http_methods(['GET'])
def consultar_cep(request):
    """
    API para consultar CEP via ViaCEP.
    
    Endpoint público (sem autenticação) para ser usado nos formulários
    de cadastro de alunos, professores, secretaria, etc.
    
    Uso: GET /academico/api/consultar-cep/?cep=01310100
    
    Retorna:
        JsonResponse: Dados do endereço ou mensagem de erro
    """
    cep = request.GET.get('cep', '')
    
    # Remove caracteres não numéricos do CEP
    cep = ''.join(filter(str.isdigit, cep))
    
    # Valida se o CEP tem 8 dígitos
    if len(cep) != 8:
        return JsonResponse({
            'erro': True,
            'mensagem': 'CEP inválido. Digite 8 dígitos.'
        }, status=400)
    
    try:
        # Faz a requisição para o ViaCEP
        url = f'https://viacep.com.br/ws/{cep}/json/'
        resposta = requests.get(url, timeout=5)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            
            # Verifica se o CEP foi encontrado
            if 'erro' in dados:
                return JsonResponse({
                    'erro': True,
                    'mensagem': 'CEP não encontrado.'
                }, status=404)
            
            # Retorna os dados do endereço
            return JsonResponse({
                'erro': False,
                'logradouro': dados.get('logradouro', ''),
                'complemento': dados.get('complemento', ''),
                'bairro': dados.get('bairro', ''),
                'cidade': dados.get('localidade', ''),
                'estado': dados.get('uf', ''),
                'cep': dados.get('cep', '')
            })
        else:
            return JsonResponse({
                'erro': True,
                'mensagem': 'Erro ao consultar CEP no servidor externo.'
            }, status=500)
            
    except requests.exceptions.Timeout:
        return JsonResponse({
            'erro': True,
            'mensagem': 'Tempo de consulta excedido. Tente novamente.'
        }, status=408)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'erro': True,
            'mensagem': f'Erro na conexão com o servidor de CEP: {str(e)}'
        }, status=503)
    except Exception as e:
        return JsonResponse({
            'erro': True,
            'mensagem': f'Erro inesperado: {str(e)}'
        }, status=500)
