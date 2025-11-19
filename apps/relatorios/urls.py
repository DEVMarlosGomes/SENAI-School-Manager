from django.urls import path
from . import views

urlpatterns = [
    path('aluno/<int:aluno_id>/pdf/', views.relatorio_aluno_pdf, name='relatorio_aluno_pdf'),
    path('professor/<int:professor_id>/pdf/', views.relatorio_professor_pdf, name='relatorio_professor_pdf'),
    path('secretaria/<int:secretaria_id>/pdf/', views.relatorio_secretaria_pdf, name='relatorio_secretaria_pdf'),
    path('coordenacao/<int:coordenacao_id>/pdf/', views.relatorio_coordenacao_pdf, name='relatorio_coordenacao_pdf'),
]
