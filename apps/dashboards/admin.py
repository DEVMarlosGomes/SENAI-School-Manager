from django.contrib import admin
from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
	list_display = ('titulo', 'disciplina', 'tipo', 'autor', 'criado_em')
	list_filter = ('tipo', 'disciplina')
	search_fields = ('titulo', 'descricao', 'disciplina')
	readonly_fields = ('criado_em',)
