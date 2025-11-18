from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

# Mapeamento das permissões por grupo (alterar os codenames conforme sua configuração)
permissoes_por_grupo = {
    'Aluno': [
        'delete_aluno', 'view_aluno',
        'add_boletim', 'change_boletim', 'delete_boletim', 'view_boletim',
        'view_historico', 'view_ocorrencia'
    ],
    'Professor': [
        'add_professor', 'change_professor', 'delete_professor', 'view_professor',
        'add_registro_ocorrencia', 'change_registro_ocorrencia', 'delete_registro_ocorrencia', 'view_registro_ocorrencia'
        # Adicione outras permissões específicas de professor aqui
    ],
    'Secretaria': [
        'add_turma', 'change_turma', 'delete_turma',
        'add_boletim', 'change_boletim', 'delete_boletim',
        'add_aluno', 'change_aluno', 'delete_aluno', 'view_aluno',
        'manage_professor', 'manage_secretaria', 'manage_permissoes',
        # Outras permissões administrativas gerais
    ],
    'Coordenacao': [
        'add_curso', 'change_curso', 'delete_curso', 'view_curso',
        'add_coordenacao', 'change_coordenacao', 'delete_coordenacao', 'view_coordenacao',
        'view_relatorios_gerais', 'manage_permissoes'
        # Mais permissões de gestão
    ],
    # Outros grupos e suas permissões podem ser adicionados aqui
}

def buscar_permissao(codename):
    # Busca permissão por codenames, considerando todos os aplicativos
    for app in apps.get_app_configs():
        perms = Permission.objects.filter(codename=codename, content_type__app_label=app.label)
        if perms.exists():
            return perms.first()
    return None

def criar_grupos_e_permissoes():
    for grupo_nome, permissoes in permissoes_por_grupo.items():
        grupo, criado = Group.objects.get_or_create(name=grupo_nome)
        print(f"{'Criado' if criado else 'Atualizado'} grupo: {grupo_nome}")
        grupo.permissions.clear()
        for codename in permissoes:
            perm = buscar_permissao(codename)
            if perm:
                grupo.permissions.add(perm)
                print(f"Permissão '{codename}' atribuída ao grupo '{grupo_nome}'.")
            else:
                print(f"Permissão '{codename}' NÃO encontrada.")
        grupo.save()

criar_grupos_e_permissoes()
print("Configuração de grupos e permissões concluída.")
