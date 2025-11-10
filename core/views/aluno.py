from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    context = {
        'proximas_aulas': [
            {
                'disciplina': 'Automação Industrial II',
                'professor': 'Maria Silva',
                'horario': '19:00',
                'sala': 'Lab 3'
            }
        ],
        'notas_recentes': [
            {
                'disciplina': 'Automação Industrial II',
                'media': 9.2,
                'professor': 'Maria Silva'
            },
            {
                'disciplina': 'Programação Web',
                'media': 7.0,
                'professor': 'Carlos Oliveira'
            }
        ],
        'avisos': [
            {
                'titulo': 'Alteração de Horário',
                'mensagem': 'A aula foi remarcada para o laboratório 3',
                'data': '2025-11-10'
            }
        ]
    }
    return render(request, 'dashboards/aluno_dashboard.html', context)

@login_required
def boletim(request):
    return render(request, 'aluno/boletim.html')

@login_required
def materiais_estudo(request):
    return render(request, 'aluno/materiais.html')

@login_required
def atividades(request):
    return render(request, 'aluno/atividades.html')