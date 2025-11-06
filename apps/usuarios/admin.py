from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from .models import Profile

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
