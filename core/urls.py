from django.urls import path
from .views import aluno

urlpatterns = [
    path('aluno/dashboard/', aluno.dashboard, name='aluno_dashboard'),
    path('aluno/boletim/', aluno.boletim, name='boletim'),
    path('aluno/materiais/', aluno.materiais_estudo, name='materiais_estudo'),
    path('aluno/atividades/', aluno.atividades, name='atividades'),
]