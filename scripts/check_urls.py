import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','school_manager.settings')
django.setup()
from django.urls import reverse
names = ['home','professor_dashboard','aluno_dashboard','secretaria_dashboard','coordenacao_dashboard','gestao_alunos','controle_financeiro','gestao_documentos','comunicacao_secretaria','cadastro_aluno','salvar_aluno','perfil']
for n in names:
    try:
        print(n, '->', reverse(n))
    except Exception as e:
        print(n, 'ERROR ->', e)
