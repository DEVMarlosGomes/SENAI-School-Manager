from django.urls import path
from . import views

urlpatterns = [
    path('emitir/boletim/', views.emitir_boletim, name='emitir_boletim_meu'),
    path('emitir/declaracao/', views.emitir_declaracao_matricula, name='emitir_declaracao_meu'),
    path('emitir/boletim/<int:aluno_id>/', views.emitir_boletim, name='emitir_boletim_aluno'),
    path('emitir/declaracao/<int:aluno_id>/', views.emitir_declaracao_matricula, name='emitir_declaracao_aluno'),
    path('download/<uuid:documento_id>/', views.download_documento, name='download_documento'),
    path('turma/<int:turma_id>/pdf/', views.baixar_relatorio_turma, name='baixar_relatorio_turma'),
    path('coordenacao/geral/<int:user_id>/', views.relatorio_coordenacao_pdf, name='relatorio_coordenacao_pdf'),
    path('aluno/geral/<int:aluno_id>/', views.relatorio_aluno_geral_pdf, name='relatorio_aluno_geral_pdf'),
    path('professor/geral/', views.relatorio_professor_geral_pdf, name='relatorio_professor_geral_pdf'),
    path('secretaria/geral/', views.relatorio_secretaria_geral_pdf, name='relatorio_secretaria_geral_pdf'),
]