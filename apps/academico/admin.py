from django.contrib import admin
from .models import (
    Endereco, Telefone, Disciplina, Coordenacao, Secretaria, Departamento, 
    Professor, Curso, Turma, Responsavel, Aluno, CursoDisciplina, 
    TurmaDisciplinaProfessor, Historico, Boletim, RegistroOcorrencia
)

# Registar todos os modelos para que apareçam na interface de admin
# Pode personalizar isto mais tarde, se quiser

admin.site.register(Endereco)
admin.site.register(Telefone)
admin.site.register(Disciplina)
admin.site.register(Coordenacao)
admin.site.register(Secretaria)
admin.site.register(Departamento)
admin.site.register(Professor)
admin.site.register(Curso)
admin.site.register(Turma)
admin.site.register(Responsavel)
admin.site.register(Aluno)
admin.site.register(CursoDisciplina)
admin.site.register(TurmaDisciplinaProfessor)
admin.site.register(Historico)
admin.site.register(Boletim)
admin.site.register(RegistroOcorrencia)