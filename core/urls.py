from django.urls import path
from .views import aluno, api, include

urlpatterns = [
    path('aluno/dashboard/', aluno.dashboard, name='aluno_dashboard'),
    path('aluno/boletim/', aluno.boletim, name='boletim'),
    path('aluno/materiais/', aluno.materiais_estudo, name='materiais_estudo'),
    path('aluno/atividades/', aluno.atividades, name='atividades'),
    # API - Consulta de CEP
    path('api/consultar-cep/', api.consultar_cep, name='consultar_cep'),
    # API - Relatórios em PDF
    path('relatorios/', include('apps.relatorios.urls')),
]
