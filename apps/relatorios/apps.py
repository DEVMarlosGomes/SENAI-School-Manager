import os
from django.apps import AppConfig

class RelatoriosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.relatorios'
    verbose_name = 'Relatórios'
    # Correção para o erro "multiple filesystem locations"
    path = os.path.dirname(os.path.abspath(__file__))