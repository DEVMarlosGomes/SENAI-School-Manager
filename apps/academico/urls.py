# apps/academico/urls.py

from django.urls import path
from .views import cadastro_aluno_view, salvar_aluno_view

urlpatterns = [
    # Cadastro de Alunos (acessada pelo botão 'Novo Aluno')
    path('alunos/cadastrar/', cadastro_aluno_view, name='cadastro_aluno'),
    path('alunos/salvar/', salvar_aluno_view, name='salvar_aluno'),
]