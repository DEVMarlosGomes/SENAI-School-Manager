from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from .models import Profile, PendingRegistration

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_tipo_perfil', 'is_active')
    list_filter = ('is_active', 'groups', 'profile__tipo')
    actions = ['make_active', 'make_inactive']
    
    def get_tipo_perfil(self, obj):
        return obj.profile.get_tipo_display() if hasattr(obj, 'profile') else '-'
    get_tipo_perfil.short_description = 'Tipo de Perfil'

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Ativar usuários selecionados"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Desativar usuários selecionados"

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Registra o modelo Profile separadamente para facilitar a gestão
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'cpf', 'telefone')
    list_filter = ('tipo',)
    search_fields = ('user__username', 'user__email', 'cpf', 'telefone')


# Admin para gerenciar registros pendentes
@admin.register(PendingRegistration)
class PendingRegistrationAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'email', 'tipo_solicitado_display', 'status_display', 'data_solicitacao', 'acao')
    list_filter = ('status', 'tipo_solicitado', 'data_solicitacao')
    search_fields = ('primeiro_nome', 'sobrenome', 'email', 'username', 'cpf')
    readonly_fields = ('data_solicitacao', 'data_aprovacao', 'aprovado_por', 'motivo_rejeicao')
    actions = ['aprovar_registros', 'rejeitar_registros']

    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('primeiro_nome', 'sobrenome', 'email', 'username', 'telefone', 'cpf')
        }),
        ('Solicitação', {
            'fields': ('tipo_solicitado', 'data_solicitacao')
        }),
        ('Status e Aprovação', {
            'fields': ('status', 'data_aprovacao', 'aprovado_por', 'motivo_rejeicao'),
            'classes': ('collapse',)
        }),
    )

    def nome_completo(self, obj):
        return f"{obj.primeiro_nome} {obj.sobrenome}"
    nome_completo.short_description = 'Nome Completo'

    def tipo_solicitado_display(self, obj):
        return obj.get_tipo_solicitado_display()
    tipo_solicitado_display.short_description = 'Tipo'

    def status_display(self, obj):
        colors = {
            'pendente': '#FFA500',      # Laranja
            'aprovado': '#28a745',      # Verde
            'rejeitado': '#dc3545',     # Vermelho
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def acao(self, obj):
        if obj.status == 'pendente':
            return format_html(
                '<a class="button" href="/admin/usuarios/pendingregistration/{}/approve/">Aprovar</a> '
                '<a class="button" style="background-color: #dc3545;" href="/admin/usuarios/pendingregistration/{}/reject/">Rejeitar</a>',
                obj.pk, obj.pk
            )
        return '-'
    acao.short_description = 'Ação'

    def aprovar_registros(self, request, queryset):
        for reg in queryset.filter(status='pendente'):
            try:
                reg.aprovar(request.user)
                self.message_user(request, f"✓ {reg.nome_completo} foi aprovado e um usuário foi criado.")
            except Exception as e:
                self.message_user(request, f"✗ Erro ao aprovar {reg.nome_completo}: {str(e)}", level='error')
    aprovar_registros.short_description = "Aprovar registros selecionados"

    def rejeitar_registros(self, request, queryset):
        for reg in queryset.filter(status='pendente'):
            try:
                reg.rejeitar(request.user, motivo='Rejeitado em lote pela ação do admin')
                self.message_user(request, f"✗ {reg.nome_completo} foi rejeitado.")
            except Exception as e:
                self.message_user(request, f"✗ Erro ao rejeitar {reg.nome_completo}: {str(e)}", level='error')
    rejeitar_registros.short_description = "Rejeitar registros selecionados"

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != 'pendente':
            # Se não está pendente, todos os campos são readonly
            return self.readonly_fields + ('primeiro_nome', 'sobrenome', 'email', 'username', 'telefone', 'cpf', 'tipo_solicitado')
        return self.readonly_fields
