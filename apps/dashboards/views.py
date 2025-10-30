# apps/dashboards/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

@login_required
def aluno_dashboard_view(request):
    # Lógica para obter dados do aluno logado
    return render(request, 'dashboards/aluno_dashboard.html')

@login_required
def professor_dashboard_view(request):
    # Lógica de obtenção de dados do professor
    return render(request, 'dashboards/professor_dashboard.html')

@login_required
def secretaria_dashboard_view(request):
    # Lógica de obtenção de dados do secretaria
    return render(request, 'dashboards/secretaria_dashboard.html')

@login_required
def coordenacao_dashboard_view(request):
    # Lógica de obtenção de dados do coordenador
    return render(request, 'dashboards/coodenacao_dashboard.html')

# Exemplo de view para o cadastro (será usada em apps/academico/urls.py)
# Recomendado mover esta função para apps/academico/views.py
def cadastro_aluno_view(request):
    # Renderiza o formulário de cadastro de aluno
    return render(request, 'academico/cadastro_aluno.html')