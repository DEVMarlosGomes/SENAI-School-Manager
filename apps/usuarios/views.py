from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from apps.academico.models import Aluno as AcadAluno
from .models import Profile, PendingRegistration

try:
    from core.models import Aluno as CoreAluno
except Exception:
    CoreAluno = None

def login_view(request):
    if request.method == 'POST':
        identifier = (request.POST.get('username') or '').strip()
        password = request.POST.get('password')
        user = authenticate(request, username=identifier, password=password)

        # Tentativa por CPF, matrícula etc
        if user is None and identifier:
            candidate = None
            try:
                candidate = User.objects.filter(profile__cpf=identifier).first()
            except Exception:
                candidate = None
            if not candidate:
                nums = ''.join(ch for ch in identifier if ch.isdigit())
                if nums:
                    try:
                        candidate = User.objects.filter(profile__cpf__icontains=nums).first()
                    except Exception:
                        candidate = None
            if not candidate:
                try:
                    acad_aluno = AcadAluno.objects.filter(matricula=identifier).first()
                    if acad_aluno:
                        candidate = acad_aluno.user
                except Exception:
                    candidate = candidate
            if not candidate and CoreAluno is not None:
                try:
                    core_aluno = CoreAluno.objects.filter(matricula=identifier).first()
                    if core_aluno:
                        candidate = core_aluno.user
                except Exception:
                    candidate = candidate
            if candidate:
                user = authenticate(request, username=candidate.username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            if not hasattr(user, 'profile'):
                return redirect('complete_profile')
            return redirect('redirecionar_dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('home')

def register_view(request):
    return render(request, 'usuarios/register.html')

def registro_pendente(request):
    if request.method == 'POST':
        primeiro_nome = request.POST.get('primeiro_nome', '').strip()
        sobrenome = request.POST.get('sobrenome', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        tipo_solicitado = request.POST.get('tipo_solicitado', '').strip()
        senha = request.POST.get('senha', '').strip()
        senha_confirmar = request.POST.get('senha_confirmar', '').strip()
        erros = []
        if not primeiro_nome:
            erros.append('Primeiro nome é obrigatório.')
        if not sobrenome:
            erros.append('Sobrenome é obrigatório.')
        if not email:
            erros.append('Email é obrigatório.')
        if not username:
            erros.append('Usuário é obrigatório.')
        if not tipo_solicitado:
            erros.append('Tipo de perfil é obrigatório.')
        if not senha:
            erros.append('Senha é obrigatória.')
        if senha != senha_confirmar:
            erros.append('As senhas não coincidem.')
        if len(senha) < 8:
            erros.append('A senha deve ter pelo menos 8 caracteres.')
        if User.objects.filter(username=username).exists():
            erros.append('Este usuário já está registrado.')
        if PendingRegistration.objects.filter(username=username).exists():
            erros.append('Este usuário já possui uma solicitação pendente.')
        if User.objects.filter(email=email).exists():
            erros.append('Este email já está registrado.')
        if PendingRegistration.objects.filter(email=email).exists():
            erros.append('Este email já possui uma solicitação pendente.')
        if cpf and (Profile.objects.filter(cpf=cpf).exists() or PendingRegistration.objects.filter(cpf=cpf).exists()):
            erros.append('Este CPF já está registrado.')
        if erros:
            for erro in erros:
                messages.error(request, erro)
            return render(request, 'usuarios/registro_pendente.html', {
                'primeiro_nome': primeiro_nome,
                'sobrenome': sobrenome,
                'email': email,
                'username': username,
                'telefone': telefone,
                'cpf': cpf,
                'tipo_solicitado': tipo_solicitado,
            })
        try:
            PendingRegistration.objects.create(
                primeiro_nome=primeiro_nome,
                sobrenome=sobrenome,
                email=email,
                username=username,
                telefone=telefone,
                cpf=cpf if cpf else None,
                tipo_solicitado=tipo_solicitado,
                status='pendente'
            )
            messages.success(request, f'✓ Cadastro realizado com sucesso! Sua solicitação está pendente de aprovação. Você receberá um email em {email} quando for aprovado.')
            return redirect('/')
        except Exception as e:
            messages.error(request, f'Erro ao criar registro: {str(e)}')
    return render(request, 'usuarios/registro_pendente.html')

@login_required
def redirecionar_dashboard(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'profile'):
        profile = user.profile
        if getattr(profile, 'is_aluno', False):
            return redirect('aluno_dashboard')
        if getattr(profile, 'is_professor', False):
            return redirect('professor_dashboard')
        if getattr(profile, 'is_secretaria', False):
            return redirect('secretaria_dashboard')
        if getattr(profile, 'is_coordenacao', False):
            return redirect('coordenacao_dashboard')
        logout(request)
        messages.error(request, 'Perfil não reconhecido. Entre em contato com o suporte.')
        return redirect('login')
    messages.error(request, 'Seu usuário não tem perfil cadastrado. Entre em contato com o suporte.')
    return redirect('login')

@login_required
def complete_profile(request):
    user = request.user
    if hasattr(user, 'profile'):
        return redirect('redirecionar_dashboard')
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        telefone = request.POST.get('telefone') or None
        cpf = request.POST.get('cpf') or None
        Profile.objects.create(user=user, tipo=tipo, telefone=telefone, cpf=cpf)
        messages.success(request, 'Perfil criado com sucesso.')
        return redirect('redirecionar_dashboard')
    return render(request, 'usuarios/complete_profile.html')

def home_view(request):
    return render(request, 'home.html')
