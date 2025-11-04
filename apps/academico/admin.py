from django.contrib import admin
from .models import Curso, Turma, Aluno, Matricula, Nota, Frequencia

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nivel', 'duracao', 'ativo')
    list_filter = ('nivel', 'ativo')
    search_fields = ('nome', 'descricao')

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'curso', 'ano', 'semestre', 'professor', 'ativa')
    list_filter = ('ano', 'semestre', 'ativa', 'curso')
    search_fields = ('codigo', 'curso__nome', 'professor__username')

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'get_nome', 'get_email')
    search_fields = ('matricula', 'user__first_name', 'user__last_name', 'user__email')
    
    def get_nome(self, obj):
        return obj.user.get_full_name()
    get_nome.short_description = 'Nome'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'E-mail'

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'data_matricula', 'status')
    list_filter = ('status', 'data_matricula')
    search_fields = ('aluno__matricula', 'aluno__user__first_name', 'turma__codigo')
    date_hierarchy = 'data_matricula'

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'descricao', 'valor', 'data')
    list_filter = ('data', 'valor')
    search_fields = ('matricula__aluno__matricula', 'descricao')
    date_hierarchy = 'data'

@admin.register(Frequencia)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'data', 'presenca')
    list_filter = ('data', 'presenca')
    search_fields = ('matricula__aluno__matricula',)
    date_hierarchy = 'data'
