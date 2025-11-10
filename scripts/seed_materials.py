import os
import sys
import django
from pathlib import Path

# Ensure project root is on PYTHONPATH (so `school_manager` package is importable)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_manager.settings')
django.setup()

from apps.dashboards.models import Material
from django.contrib.auth import get_user_model

User = get_user_model()

# Tenta pegar um autor existente (primeiro superuser) para associar
author = User.objects.filter(is_superuser=True).first()

samples = [
    {'titulo': 'Apostila de Automação','disciplina':'Automação Industrial II','tipo':'PDF','descricao':'Material completo sobre sistemas de automação industrial'},
    {'titulo': 'Slides - Programação Web','disciplina':'Programação Web','tipo':'PPT','descricao':'Apresentação sobre desenvolvimento web moderno'},
    {'titulo': 'Vídeo Aula - Redes Industriais','disciplina':'Redes Industriais','tipo':'Vídeo','descricao':'Gravação da aula sobre topologias de rede'},
    {'titulo': 'Guia de Segurança no Laboratório','disciplina':'Segurança do Trabalho','tipo':'PDF','descricao':'Procedimentos e normas para uso de equipamentos'},
    {'titulo': 'Exercícios Práticos - Eletrônica','disciplina':'Eletrônica','tipo':'Arquivo','descricao':'Conjunto de exercícios resolvidos'},
    {'titulo': 'Projeto - Automação Residencial','disciplina':'Automação Industrial II','tipo':'PDF','descricao':'Relatório e diagrama do projeto'},
    {'titulo': 'Manual do Aluno - Programação Web','disciplina':'Programação Web','tipo':'PDF','descricao':'Documentação auxiliar para alunos'},
    {'titulo': 'Padrões de Projeto - Backend','disciplina':'Programação Web','tipo':'PPT','descricao':'Slides sobre padrões de arquitetura backend'},
]

created = 0
for s in samples:
    obj, created_flag = Material.objects.get_or_create(
        titulo=s['titulo'],
        defaults={
            'descricao': s['descricao'],
            'disciplina': s['disciplina'],
            'tipo': s['tipo'],
            'autor': author
        }
    )
    if created_flag:
        created += 1

print(f"Seed completed. Created {created} materials.")
