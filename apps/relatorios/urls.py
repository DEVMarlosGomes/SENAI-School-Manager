from django.urls import path
from . import views

urlpatterns = [
    # Aluno (Gera para si mesmo)
    path('emitir/boletim/', views.emitir_boletim, name='emitir_boletim_meu'),
    path('emitir/declaracao/', views.emitir_declaracao_matricula, name='emitir_declaracao_meu'),
    
    # Secretaria (Gera para um aluno específico)
    path('emitir/boletim/<int:aluno_id>/', views.emitir_boletim, name='emitir_boletim_aluno'),
    path('emitir/declaracao/<int:aluno_id>/', views.emitir_declaracao_matricula, name='emitir_declaracao_aluno'),
    
    # Download Genérico (Baixa arquivo salvo)
    path('download/<uuid:documento_id>/', views.download_documento, name='download_documento'),
    
    # Professor (Lista da Turma)
    path('turma/<int:turma_id>/pdf/', views.baixar_relatorio_turma, name='baixar_relatorio_turma'),
]