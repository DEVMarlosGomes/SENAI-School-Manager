from django.contrib import admin
from .models import Material, Aviso, EventoAcademico


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
	list_display = ('titulo', 'disciplina', 'tipo', 'autor', 'criado_em')
	list_filter = ('tipo', 'disciplina')
	search_fields = ('titulo', 'descricao', 'disciplina')
	readonly_fields = ('criado_em',)


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
	list_display = ('titulo', 'tipo', 'tipo_usuario_criador', 'data_publicacao', 'ativo')
	list_filter = ('tipo', 'tipo_usuario_criador', 'ativo', 'data_publicacao')
	search_fields = ('titulo', 'conteudo')
	readonly_fields = ('data_publicacao',)
	fieldsets = (
		('Informações Básicas', {
			'fields': ('titulo', 'conteudo', 'tipo')
		}),
		('Criador e Tipo', {
			'fields': ('criado_por', 'tipo_usuario_criador')
		}),
		('Visibilidade', {
			'fields': ('ativo', 'data_inicio_visibilidade', 'data_fim_visibilidade', 'data_publicacao')
		}),
	)


@admin.register(EventoAcademico)
class EventoAcademicoAdmin(admin.ModelAdmin):
	list_display = ('titulo', 'data_evento', 'tipo_usuario_criador', 'local', 'ativo')
	list_filter = ('data_evento', 'tipo_usuario_criador', 'ativo')
	search_fields = ('titulo', 'descricao', 'local')
	readonly_fields = ('data_criacao',)
	fieldsets = (
		('Informações do Evento', {
			'fields': ('titulo', 'descricao', 'data_evento', 'local')
		}),
		('Criador', {
			'fields': ('criado_por', 'tipo_usuario_criador')
		}),
		('Status', {
			'fields': ('ativo', 'data_criacao')
		}),
	)
