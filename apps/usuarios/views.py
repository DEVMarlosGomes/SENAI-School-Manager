# apps/usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from .models import Profile, PendingRegistration
from apps.academico.models import Aluno, Professor

@never_cache
@csrf_protect
def login_view(request):
    if request.method == 'POST':
        identifier = (request.POST.get('username') or '').strip()
        password = request.POST.get('password')
        
        user = authenticate(request, username=identifier, password=password)
        
        if user is None:
             try:
                 u = User.objects.get(username=identifier)
                 user = authenticate(request, username=u.username, password=password)
             except User.DoesNotExist:
                 pass

        if user is not None:
            login(request, user)
            # Verifica para onde ir
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('redirecionar_dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'usuarios/login.html')

@never_cache
def logout_view(request):
    logout(request)
    return redirect('home')

@csrf_protect
def register_view(request):
    return render(request, 'usuarios/register.html')

@csrf_protect
def registro_pendente(request):
    if request.method == 'POST':
        primeiro_nome = request.POST.get('primeiro_nome', '').strip()
        sobrenome = request.POST.get('sobrenome', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        senha = request.POST.get('senha', '').strip()
        senha_confirmar = request.POST.get('senha_confirmar', '').strip()
        tipo_solicitado = request.POST.get('tipo_solicitado', '').strip()
        
        telefone = request.POST.get('telefone', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        cep = request.POST.get('cep', '').strip()
        logradouro = request.POST.get('logradouro', '').strip()
        numero = request.POST.get('numero', '').strip()
        bairro = request.POST.get('bairro', '').strip()
        cidade = request.POST.get('cidade', '').strip()
        estado = request.POST.get('estado', '').strip()
        
        if senha != senha_confirmar:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'usuarios/registro_pendente.html')
            
        if User.objects.filter(username=username).exists():
             messages.error(request, 'Este nome de usuário já está em uso.')
             return render(request, 'usuarios/registro_pendente.html')

        if cpf and PendingRegistration.objects.filter(cpf=cpf).exclude(status='rejeitado').exists():
            messages.error(request, 'Já existe uma solicitação com este CPF.')
            return render(request, 'usuarios/registro_pendente.html')

        try:
            PendingRegistration.objects.create(
                primeiro_nome=primeiro_nome, 
                sobrenome=sobrenome, 
                email=email,
                username=username, 
                senha=senha,
                tipo_solicitado=tipo_solicitado,
                telefone=telefone,
                cpf=cpf if cpf else None,
                cep=cep, logradouro=logradouro, numero=numero,
                bairro=bairro, cidade=cidade, estado=estado,
                status='pendente'
            )
            messages.success(request, '✅ Solicitação enviada! Aguarde a aprovação.')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Erro no sistema: {str(e)}')
    
    return render(request, 'usuarios/registro_pendente.html')

@login_required
def redirecionar_dashboard(request):
    """
    Função central de roteamento. NUNCA deve fazer logout automático.
    """
    user = request.user
    
    # 1. Se for Superusuário (Admin), manda para o painel administrativo
    if user.is_superuser or user.is_staff:
        # Verifica se ele tem perfil também, se tiver, segue fluxo normal
        if not hasattr(user, 'profile'):
            return redirect('/admin/')

    # 2. Se não tem perfil, manda completar (NÃO desloga)
    if not hasattr(user, 'profile'):
        return redirect('complete_profile')
        
    # 3. Verifica o tipo e manda para o dashboard correto
    try:
        profile = user.profile
        tipo = profile.tipo
        
        # Validação de dados incompletos para Aluno/Professor
        dados_incompletos = False
        if tipo == 'aluno':
            try:
                aluno = Aluno.objects.get(user=user)
                if not aluno.data_nascimento or not aluno.RG_aluno:
                    dados_incompletos = True
            except Aluno.DoesNotExist:
                dados_incompletos = True
                
        elif tipo == 'professor':
            try:
                prof = Professor.objects.get(user=user)
                if not prof.formacao or not prof.registro_funcional:
                    dados_incompletos = True
            except Professor.DoesNotExist:
                dados_incompletos = True

        if dados_incompletos:
            messages.info(request, "Faltam alguns dados no seu cadastro. Vamos completar?")
            return redirect('complete_profile')

        # Redirecionamento final
        if tipo == 'aluno': return redirect('aluno_dashboard')
        if tipo == 'professor': return redirect('professor_dashboard')
        if tipo == 'secretaria': return redirect('secretaria_dashboard')
        if tipo == 'coordenacao': return redirect('coordenacao_dashboard')
        
    except Exception as e:
        print(f"Erro no redirecionamento: {e}")
    
    # 4. Fallback de Segurança: Se nada funcionar, manda para Home
    messages.warning(request, "Perfil acessado não possui um dashboard específico.")
    return redirect('home')

@login_required
def complete_profile(request):
    user = request.user
    # Se não tem perfil, assume aluno por padrão ou pede para escolher (simplificado para aluno)
    if not hasattr(user, 'profile'):
        tipo = 'aluno'
    else:
        tipo = user.profile.tipo

    if request.method == 'POST':
        try:
            # Garante que o Profile existe
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user, tipo=tipo)
            
            if tipo == 'aluno':
                aluno, _ = Aluno.objects.get_or_create(user=user, defaults={'RA_aluno': user.username})
                aluno.data_nascimento = request.POST.get('data_nascimento')
                aluno.RG_aluno = request.POST.get('rg')
                aluno.genero = request.POST.get('genero')
                aluno.estado_civil = request.POST.get('estado_civil')
                aluno.save()
                
            elif tipo == 'professor':
                prof, _ = Professor.objects.get_or_create(user=user)
                prof.data_contratacao = request.POST.get('data_contratacao')
                prof.formacao = request.POST.get('formacao')
                prof.registro_funcional = request.POST.get('registro_funcional') or user.username
                prof.tipo_vinculo = request.POST.get('tipo_vinculo')
                prof.save()

            messages.success(request, "Dados atualizados!")
            return redirect('redirecionar_dashboard')
            
        except Exception as e:
            messages.error(request, f"Erro: {str(e)}")

    return render(request, 'usuarios/complete_profile.html', {'tipo': tipo})

def politica_privacidade(request): return render(request, 'politica_privacidade.html')
def termos_uso(request): return render(request, 'termos_uso.html')