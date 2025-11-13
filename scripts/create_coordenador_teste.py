#!/usr/bin/env python
"""
Script para criar um usuário coordenador de teste
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_manager.settings')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import Profile

# Dados do coordenador
username = 'coordenador_teste'
email = 'coordenador@teste.br'
password = 'Senha123!'

# Verificar se usuário já existe
if User.objects.filter(username=username).exists():
    print(f'✗ Usuário {username} já existe')
    exit(1)

# Criar usuário
user = User.objects.create_user(
    username=username,
    email=email,
    password=password,
    first_name='Coordenador',
    last_name='Teste'
)

# Criar/atualizar profile
profile, created = Profile.objects.get_or_create(user=user)
profile.tipo = 'coordenacao'
profile.save()

print(f'✓ Usuário criado com sucesso!')
print(f'  Username: {username}')
print(f'  Email: {email}')
print(f'  Senha: {password}')
print(f'  Tipo: Coordenador')
print(f'\nPerfil: {"Criado" if created else "Atualizado"}')
