from django.contrib import admin
from .models import Aluno, Curso, Professor, Disciplina

admin.site.register(Aluno)
admin.site.register(Curso)
admin.site.register(Professor)
admin.site.register(Disciplina)